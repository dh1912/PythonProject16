"""Thao tác chuột/phím thật trên game WASM với API và SQLite tạm, không HTTP mock."""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import sqlite3
from contextlib import closing
from urllib.parse import urlsplit


def main() -> int:
    from playwright.sync_api import sync_playwright
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='task5-ui-') as directory:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        url = f'http://127.0.0.1:{port}'
        env = dict(os.environ, SQLITE_DB_PATH=str(Path(directory) / 'ui.db'),
                   JWT_SECRET=secrets.token_urlsafe(48), PYTHONUTF8='1',
                   WEB_BUILD_DIR=str(root / 'build/web-source/build/web'))
        transaction_mode = os.getenv('TASK5_TRANSACTION_MODE', '')
        if transaction_mode:
            mapping = {'/progress/save':'save_progress','/quiz/submit':'submit_answer',
                       '/clues/collect':'collect_clue','/quest/complete':'complete_quest',
                       '/review/retry':'retry_review'}
            env.update(TASK5_TRANSACTION_BARRIER=directory,
                       TASK5_TRANSACTION_FUNCTION=mapping[os.environ['TASK5_ISOLATION_ENDPOINT']],
                       TASK5_TEST_PORT=str(port),
                       TASK5_TRANSACTION_ROLLBACK='1' if transaction_mode == 'rollback' else '0')
        # Log nằm ngoài DB tạm: Windows/antivirus có thể giữ handle sau terminate.
        with (root / 'data/sqlite-ui-server.log').open('w', encoding='utf-8') as log:
            command = [sys.executable, '-m', 'task5.test_transaction_server'] if transaction_mode else [sys.executable, '-m', 'uvicorn', 'task5.server.app:app',
                                       '--host', '127.0.0.1', '--port', str(port)]
            server = subprocess.Popen(command,
                                      cwd=root, env=env, stdout=log, stderr=log)
            try:
                for _ in range(80):
                    try:
                        with urllib.request.urlopen(url + '/api/health', timeout=1):
                            break
                    except OSError:
                        time.sleep(.25)
                else:
                    raise RuntimeError('API SQLite chưa sẵn sàng.')
                with sync_playwright() as pw:
                    options = {'channel': 'msedge'} if sys.platform == 'win32' else {}
                    browser = pw.chromium.launch(headless=True, **options)
                    try:
                        page = browser.new_page(viewport={'width': 1280, 'height': 900})
                        errors: list[str] = []
                        diagnostic: dict = {'network': [], 'clicks': [], 'errors': errors,
                                            'console_errors': [], 'requestfailed': []}
                        started = time.monotonic()
                        def network(event: str, request, status=None):
                            path = urlsplit(request.url).path
                            if not request.url.startswith(url):
                                return
                            diagnostic['network'].append({'event': event, 'path': path,
                                'method': request.method, 'status': status,
                                'seconds': round(time.monotonic() - started, 3)})
                        def request_started(request):
                            network('request', request)
                            if urlsplit(request.url).path == '/auth/login':
                                # Chỉ lưu kết quả so khớp, không lưu body, mật khẩu hoặc hash.
                                body = request.post_data_json
                                diagnostic['credentials_received'] = {
                                    'username_matches': body.get('username') == username,
                                    'password_matches': body.get('password') == password,
                                    'username_lowercase_matches': body.get('username') == username.lower(),
                                    'password_lowercase_matches': body.get('password') == password.lower()}
                            if urlsplit(request.url).path == '/quiz/submit':
                                diagnostic.setdefault('session_submissions', []).append(
                                    bool(request.post_data_json.get('session_id')))
                        def request_failed(request):
                            network('failed', request)
                            diagnostic['requestfailed'].append({'path': urlsplit(request.url).path,
                                                                 'failure': request.failure})
                        page.on('request', request_started)
                        page.on('requestfailed', request_failed)
                        page.on('pageerror', lambda exc: errors.append(str(exc)))
                        page.on('response', lambda response: network('response', response.request, response.status))
                        page.on('console', lambda msg: diagnostic['console_errors'].append(msg.text)
                                if msg.type == 'error' and 'Bearer ' not in msg.text else None)
                        username = 'ui_qQ_' + secrets.token_hex(5)
                        password = ' ui-qQ-test-password-' + secrets.token_hex(5) + ' '
                        registration = page.request.post(url + '/auth/register', data={
                            'username': username, 'password': password, 'fullname': 'UI Acceptance'})
                        assert registration.status == 201
                        headers = {'Authorization': 'Bearer ' + registration.json()['access_token']}
                        content = page.request.get(url + '/game/content').json()
                        # Đáp án fixture đọc từ nguồn repository, không lấy từ API công khai.
                        from data.content_v6 import extract_official_sources
                        official = extract_official_sources(root)['cau_hoi_on_tap']
                        answers = {q['noi_dung_cau_hoi']: ord(q['dap_an_dung'])-65 for q in official}
                        legacy = json.loads((root / 'data/historical_seed.json').read_text(encoding='utf-8'))
                        answers.update({q['noi_dung_cau_hoi']: ord(q['dap_an_dung'])-65 for q in legacy['cau_hoi_on_tap']})
                        for items in content['questions'].values():
                            for q in items:
                                assert 'answer' not in q and 'explanation' not in q
                                q['answer'] = answers[q['question']]
                        loc = next(item for item in content['locations'] if item['id'] == 1)
                        isolation_endpoint = os.getenv('TASK5_ISOLATION_ENDPOINT', '')
                        allowed_isolation = ('/quiz/submit','/clues/collect','/quest/complete','/review/retry','/progress/save')
                        if isolation_endpoint and isolation_endpoint not in allowed_isolation:
                            raise ValueError('Endpoint nghiệm thu không hợp lệ')
                        isolation_held = []
                        if isolation_endpoint:
                            def hold_isolation(route):
                                if transaction_mode:
                                    isolation_held.append((route,None))
                                    route.continue_()
                                    return
                                if os.getenv('TASK5_REFRESH_BEFORE_BACKEND') == '1':
                                    isolation_held.append((route,None))
                                    return
                                response = route.fetch()
                                assert response.ok, f'Backend từ chối {isolation_endpoint}'
                                isolation_held.append((route,response))
                            page.route('**'+isolation_endpoint,hold_isolation,times=1)
                        page.goto(url + '/web/?acceptance=1', wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true', timeout=120000)
                        page.wait_for_timeout(1500)
                        canvas = page.locator('#canvas')

                        def click(x: float, y: float) -> None:
                            page.wait_for_function("document.querySelector('#canvas').width > 0 && document.querySelector('#canvas').height > 0", timeout=15000)
                            box = canvas.bounding_box()
                            assert box
                            w, h = canvas.evaluate('c=>[c.width,c.height]')
                            scale = min(w / 1080, h / 720)
                            diagnostic['clicks'].append({'logical': [x, y], 'canvas': [w, h],
                                'box': box, 'active_element': page.evaluate('document.activeElement.tagName')})
                            canvas.click(position={
                                'x': ((w - 1080 * scale) / 2 + x * scale) * box['width'] / w,
                                'y': ((h - 720 * scale) / 2 + y * scale) * box['height'] / h})

                        def progress() -> dict:
                            response = page.request.get(url + '/progress/me', headers=headers)
                            assert response.ok
                            return response.json()['data']

                        def type_credentials(text: str) -> None:
                            """SDL Linux đọc modifier KEYDOWN: gửi Shift thật thay vì chỉ JS key='Q'."""
                            for char in text:
                                if char.isascii() and char.isalpha() and char.isupper():
                                    page.keyboard.down('Shift')
                                    page.wait_for_timeout(100)
                                    page.keyboard.press(char, delay=100)
                                    page.wait_for_timeout(100)
                                    page.keyboard.up('Shift')
                                else:
                                    page.keyboard.type(char, delay=40)
                                page.wait_for_timeout(40)

                        def finish_isolation() -> int:
                            """Logout/login bằng canvas; chỉ fixture tài khoản được tạo qua HTTP."""
                            for _ in range(100):
                                if isolation_held: break
                                page.wait_for_timeout(100)
                            assert isolation_held, 'Chưa có request UI thật được commit'
                            if transaction_mode:
                                for _ in range(300):
                                    if (Path(directory)/'entered').exists(): break
                                    page.wait_for_timeout(50)
                                assert (Path(directory)/'entered').exists(), 'Chưa vào transaction'
                                # WAL reader độc lập thấy dữ liệu trước commit.
                                baseline = progress()
                                baseline_reviews = page.request.get(url+'/review/me',headers=headers).json()
                                page.reload(wait_until='domcontentloaded')
                                (Path(directory)/'release').write_text('release',encoding='ascii')
                                for _ in range(300):
                                    if (Path(directory)/'finished').exists(): break
                                    page.wait_for_timeout(50)
                                assert (Path(directory)/'finished').read_text() == transaction_mode
                                committed = progress()
                                if transaction_mode == 'rollback':
                                    assert committed == baseline
                                    assert page.request.get(url+'/review/me',headers=headers).json() == baseline_reviews
                                page.wait_for_function('window.task5GameReady === true',timeout=120000)
                                page.wait_for_timeout(1000)
                                click(500,280); type_credentials(username)
                                click(500,355); type_credentials(password)
                                with page.expect_response(lambda r:r.url.endswith('/auth/login')) as logged:
                                    click(500,432)
                                assert logged.value.status == 200
                                page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                                assert progress() == committed
                                assert json.loads(page.evaluate('window.task5UiState'))['score'] == committed['score']
                                assert not errors,errors
                                result={'endpoint':isolation_endpoint,'in_transaction':transaction_mode,
                                        'canvas_relogin':True,'page_errors':errors}
                                (root/f"data/transaction-{transaction_mode}-{isolation_endpoint.rsplit('/',1)[-1]}.json").write_text(
                                    json.dumps(result,indent=2),encoding='utf-8')
                                print(json.dumps(result))
                                return 0
                            # Snapshot đầy đủ giúp phát hiện cập nhật nhầm cả review và clue.
                            before_a = progress()
                            reviews_a = page.request.get(url+'/review/me',headers=headers).json()
                            if os.getenv('TASK5_REFRESH_AFTER_COMMIT') == '1' or os.getenv('TASK5_REFRESH_BEFORE_BACKEND') == '1':
                                page.reload(wait_until='domcontentloaded')
                                page.wait_for_function('window.task5GameReady === true',timeout=120000)
                                for route,response in isolation_held:
                                    try:
                                        if response is None: route.abort('connectionfailed')
                                        else: route.fulfill(response=response)
                                    except Exception: pass
                                page.wait_for_timeout(1200)
                                click(500,280)
                                type_credentials(username)
                                click(500,355)
                                type_credentials(password)
                                with page.expect_response(lambda r:r.url.endswith('/auth/login')) as relogged:
                                    click(500,432)
                                assert relogged.value.status == 200
                                page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                                page.wait_for_timeout(800)
                                assert progress() == before_a
                                assert page.request.get(url+'/review/me',headers=headers).json() == reviews_a
                                assert json.loads(page.evaluate('window.task5UiState'))['score'] == before_a['score']
                                assert not errors,errors
                                phase = 'before_backend' if os.getenv('TASK5_REFRESH_BEFORE_BACKEND') == '1' else 'after_commit'
                                result={'endpoint':isolation_endpoint,'canvas_refresh_phase':phase,
                                        'progress_and_reviews_restored':True,'page_errors':errors}
                                name=isolation_endpoint.rsplit('/',1)[-1]
                                (root/f'data/refresh-{phase}-{name}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                                print(json.dumps(result))
                                return 0
                            for _ in range(4):
                                current = json.loads(page.evaluate('window.task5UiState'))['scene']
                                if current == 'map': break
                                page.keyboard.press('Escape')
                                page.wait_for_timeout(400)
                            assert json.loads(page.evaluate('window.task5UiState'))['scene'] == 'map'
                            page.keyboard.press('l')
                            page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'login'")
                            b = {'username':'ab_'+secrets.token_hex(5),'password':'Bb_'+secrets.token_hex(7)}
                            registered = page.request.post(url+'/auth/register',data={**b,'fullname':'Isolation B'})
                            assert registered.status == 201
                            bh = {'Authorization':'Bearer '+registered.json()['access_token']}
                            click(500,280)
                            for _ in range(60): page.keyboard.press('Backspace')
                            type_credentials(b['username'])
                            click(500,355)
                            for _ in range(72): page.keyboard.press('Backspace')
                            type_credentials(b['password'])
                            with page.expect_response(lambda r:r.url.endswith('/auth/login')) as logged:
                                click(500,432)
                            assert logged.value.status == 200
                            page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                            for route,response in isolation_held:
                                try: route.fulfill(response=response)
                                except Exception: pass  # Fetch A có thể đã bị logout hủy.
                            page.wait_for_timeout(1200)
                            ui = json.loads(page.evaluate('window.task5UiState'))
                            assert ui['score'] == 0 and ui['completed_count'] == 0
                            assert ui['save_state'] == 'confirmed'
                            bp = page.request.get(url+'/progress/me',headers=bh).json()['data']
                            assert bp['score'] == 0 and not bp['completed'] and not bp['task4']
                            assert not page.request.get(url+'/review/me',headers=bh).json()['items']
                            assert progress() == before_a
                            assert page.request.get(url+'/review/me',headers=headers).json() == reviews_a
                            with closing(sqlite3.connect(Path(directory)/'ui.db')) as verify:
                                assert verify.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
                                assert not verify.execute('PRAGMA foreign_key_check').fetchall()
                            assert not errors, errors
                            name=isolation_endpoint.rsplit('/',1)[-1]
                            page.screenshot(path=str(root/f'data/isolation-{name}.png'))
                            result={'endpoint':isolation_endpoint,'canvas_account_isolation':True,
                                    'backend_committed_for_A':True,'B_unchanged':True,'page_errors':errors}
                            (root/f'data/isolation-{name}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                            print(json.dumps(result))
                            return 0

                        # Chỉ tạo fixture bằng HTTP; toàn bộ hành động chơi dưới đây qua UI.
                        click(500, 280)
                        type_credentials(username)
                        if sys.platform == 'win32':
                            page.keyboard.press('Tab')
                        else:
                            click(500, 355)
                        type_credentials(password)
                        page.keyboard.type('x')
                        page.keyboard.press('Backspace')
                        with page.expect_response(lambda r: r.url.endswith('/auth/login')) as auth_response:
                            if sys.platform == 'win32':
                                page.keyboard.press('Enter')
                            else:
                                click(500, 432)
                        assert auth_response.value.status == 200, f'Login HTTP {auth_response.value.status}'
                        assert diagnostic['credentials_received']['username_matches']
                        assert diagnostic['credentials_received']['password_matches']
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'", timeout=15000)
                        review_responses = [entry for entry in diagnostic['network']
                                            if entry['path'] == '/review/me' and entry['event'] == 'response']
                        assert review_responses and review_responses[-1]['status'] == 200, 'Review chưa tải thành công'
                        page.wait_for_timeout(1500)
                        before = progress()
                        page.keyboard.press('n')
                        page.wait_for_timeout(1200)
                        page.screenshot(path=str(root / 'data/sqlite-ui-notebook.png'))
                        assert progress() == before, 'Mở Notebook không được tăng tiến độ/điểm.'
                        page.keyboard.press('Escape')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                        click(loc['x'], loc['y'])
                        page.keyboard.press('Enter')
                        if isolation_endpoint == '/progress/save':
                            return finish_isolation()
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'investigation'")
                        for index in range(len(content['investigation_data'][loc['name']]['clues'])):
                            page.keyboard.press(str(index + 1))
                            page.wait_for_timeout(200)
                            for choice in ('1', '2', '3'):
                                page.keyboard.press(choice)
                                page.wait_for_timeout(500)
                                if isolation_endpoint == '/clues/collect' and isolation_held:
                                    return finish_isolation()
                        page.keyboard.press('d')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'deduction'")
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').question_ready === true")
                        questions = content['questions'][loc['name']]
                        page.wait_for_timeout(500)
                        q = questions[0]
                        if isolation_endpoint == '/quiz/submit':
                            page.keyboard.press(str((q['answer'] + 1) % 4 + 1))
                            return finish_isolation()
                        with page.expect_response(lambda r: r.url.endswith('/quiz/submit') and r.ok):
                            page.keyboard.press(str((q['answer'] + 1) % 4 + 1))
                        page.wait_for_timeout(700)
                        # Sai không được hoàn thành quest; thử lại đúng trên cùng câu.
                        assert not progress()['completed']
                        for q in questions:
                            with page.expect_response(lambda r: r.url.endswith('/quiz/submit') and r.ok):
                                page.keyboard.press(str(q['answer'] + 1))
                            page.wait_for_timeout(700)
                        if isolation_endpoint == '/quest/complete':
                            return finish_isolation()
                        for _ in range(60):
                            if loc['name'] in progress()['completed']:
                                break
                            page.wait_for_timeout(250)
                        else:
                            raise AssertionError('UI quest không được server xác nhận.')
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(500)
                        page.keyboard.press('r')
                        page.wait_for_timeout(800)
                        if isolation_endpoint == '/review/retry':
                            page.keyboard.press(str(questions[0]['answer'] + 1))
                            return finish_isolation()
                        with page.expect_response(lambda r: r.url.endswith('/review/retry') and r.ok):
                            page.keyboard.press(str(questions[0]['answer'] + 1))
                        page.wait_for_timeout(800)
                        reviews = page.request.get(url + '/review/me', headers=headers).json()['items']
                        assert any(q['status'] == 'MASTERED' for q in reviews)
                        page.keyboard.press('Escape')
                        page.wait_for_timeout(500)
                        with page.expect_response(lambda r: r.url.endswith('/leaderboard') and r.ok):
                            page.keyboard.press('b')
                        page.wait_for_timeout(700)
                        page.screenshot(path=str(root / 'data/sqlite-ui-board.png'))
                        page.keyboard.press('Escape')
                        page.wait_for_timeout(500)
                        next_loc = next(item for item in content['locations'] if item['id'] == 2)
                        click(next_loc['x'], next_loc['y'])
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(1000)
                        page.screenshot(path=str(root / 'data/sqlite-ui-next.png'))
                        # Fixture DB chỉ mở khóa các mốc cho test canvas; không dùng làm bằng chứng
                        # hoàn thành những quest trước đó. Mỗi quest đích vẫn thu clue/chấm/complete thật.
                        from task4.timeline_data import TIMELINE_QUEST_CONFIGS
                        timeline_results = []
                        def state():
                            return json.loads(page.evaluate('window.task5UiState'))
                        def logical_position(x, y):
                            box=canvas.bounding_box();w,h=canvas.evaluate('c=>[c.width,c.height]')
                            scale=min(w/1080,h/720)
                            return (box['x']+((w-1080*scale)/2+x*scale)*box['width']/w,
                                    box['y']+((h-720*scale)/2+y*scale)*box['height']/h)
                        for target_id in (4,6,8,9):
                            target=next(item for item in content['locations'] if item['id']==target_id)
                            completed=[item['name'] for item in content['locations'] if item['id']!=target_id]
                            db=sqlite3.connect(env['SQLITE_DB_PATH'])
                            db.execute('UPDATE tien_do_choi SET danh_sach_dia_diem_da_mo=?,ma_dia_diem_hien_tai=1 WHERE ma_nguoi_dung=?',
                                       (json.dumps(completed),registration.json()['user']['ma_nguoi_dung']))
                            db.commit();db.close()
                            page.reload(wait_until='domcontentloaded')
                            page.wait_for_function('window.task5GameReady === true',timeout=120000)
                            page.wait_for_timeout(1500)
                            click(500,280);type_credentials(username)
                            click(500,355);type_credentials(password)
                            with page.expect_response(lambda r:r.url.endswith('/review/me') and r.ok):click(500,432)
                            page.wait_for_timeout(1400)
                            # Hai pin Bến Nhà Rồng/Dinh cách 16px; chọn mép phải pin Dinh
                            # tránh hit pin Bến trước trong danh sách mà không gọi Game trực tiếp.
                            click(target['x']+(15 if target_id==9 else 0),target['y'])
                            page.keyboard.press('Enter')
                            page.wait_for_function("JSON.parse(window.task5UiState).scene === 'investigation'")
                            page.wait_for_timeout(800)
                            for index in range(len(content['investigation_data'][target['name']]['clues'])):
                                page.keyboard.press(str(index+1));page.wait_for_timeout(150)
                                for choice in ('1','2','3'):
                                    page.keyboard.press(choice);page.wait_for_timeout(450)
                            page.keyboard.press('d');page.wait_for_timeout(900)
                            assert state()['scene']=='task4_timeline',target['name']
                            for index in range(4):
                                start=logical_position(200,150+index*105)
                                end=logical_position(700,150+index*105)
                                page.mouse.move(*start);page.mouse.down()
                                page.mouse.move(*end,steps=10);page.mouse.up();page.wait_for_timeout(150)
                            page.keyboard.press('Enter')
                            page.wait_for_function("JSON.parse(window.task5UiState).scene === 'task4_quiz'")
                            submissions_before=len(diagnostic.get('session_submissions',[]))
                            for index,q in enumerate(TIMELINE_QUEST_CONFIGS[target['name']]['questions']):
                                page.wait_for_function("JSON.parse(window.task5UiState).quiz_index === "+str(index))
                                page.wait_for_timeout(700)
                                with page.expect_response(lambda r:r.url.endswith('/quiz/submit') and r.ok):
                                    page.keyboard.press(str(q['answer']+1))
                            for _ in range(60):
                                if target['name'] in progress()['completed']:break
                                page.wait_for_timeout(250)
                            else:raise AssertionError('Timeline quest chưa confirmed '+target['name'])
                            assert diagnostic['session_submissions'][submissions_before:]==[True,True,True]
                            timeline_results.append(target['name'])
                        # Response save của A đã commit, giữ lại trước khi chuyển tài khoản bằng UI.
                        page.keyboard.press('Escape')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'investigation'")
                        page.keyboard.press('Escape')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                        account_b = {'username': 'isolation_'+secrets.token_hex(5),
                                     'password': 'Bb_'+secrets.token_hex(8)}
                        registered_b = page.request.post(url+'/auth/register', data={
                            **account_b, 'fullname': 'Tài khoản cách ly B'})
                        assert registered_b.status == 201
                        held = []
                        def hold_save(route):
                            response = route.fetch()
                            assert response.ok
                            held.append((route, response))
                        page.route('**/progress/save', hold_save, times=1)
                        click(next_loc['x'], next_loc['y'])
                        page.keyboard.press('Enter')
                        for _ in range(100):
                            if held: break
                            page.wait_for_timeout(100)
                        assert held, 'UI phải thực sự gửi save trước khi đổi tài khoản'
                        a_after_commit = progress()
                        page.keyboard.press('Escape')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                        page.keyboard.press('l')
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'login'")
                        click(500, 280)
                        page.keyboard.press('Control+a')
                        # InputBox không hỗ trợ chọn tất cả: xóa bằng Backspace thật.
                        for _ in range(60): page.keyboard.press('Backspace')
                        type_credentials(account_b['username'])
                        click(500, 355)
                        for _ in range(72): page.keyboard.press('Backspace')
                        type_credentials(account_b['password'])
                        with page.expect_response(lambda r:r.url.endswith('/auth/login')) as login_b:
                            click(500, 432)
                        assert login_b.value.status == 200
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                        for route, response in held:
                            try:
                                route.fulfill(response=response)
                            except Exception:
                                # Logout đã hủy fetch phía client; commit của A vẫn hợp lệ.
                                pass
                        page.wait_for_timeout(1000)
                        state_b = json.loads(page.evaluate('window.task5UiState'))
                        assert state_b['score'] == 0 and state_b['completed_count'] == 0
                        assert state_b['save_state'] == 'confirmed'
                        logged_b = page.request.post(url+'/auth/login', data=account_b)
                        assert logged_b.status == 200
                        b_headers = {'Authorization':'Bearer '+logged_b.json()['access_token']}
                        b_progress = page.request.get(url+'/progress/me', headers=b_headers).json()['data']
                        assert b_progress['score'] == 0 and not b_progress['completed']
                        assert progress() == a_after_commit
                        page.screenshot(path=str(root/'data/sqlite-ui-isolation.png'))
                        hud_evidence = []
                        for width, height in ((1280,900),(1366,768),(1920,1080)):
                            page.set_viewport_size({'width':width,'height':height})
                            page.wait_for_timeout(600)
                            assert json.loads(page.evaluate('window.task5UiState'))['save_state'] == 'confirmed'
                            image = f'data/hud-map-confirmed-{width}x{height}.png'
                            page.screenshot(path=str(root/image))
                            hud_evidence.append({'scene':'map','state':'confirmed',
                                'viewport':[width,height],'screenshot':image,
                                'result':'CAPTURED_REQUIRES_VISUAL_REVIEW'})
                        page.set_viewport_size({'width':1280,'height':900})
                        # Refresh sau commit thật nhưng trước response; không phát lại save tự động.
                        held.clear()
                        page.route('**/progress/save', hold_save, times=1)
                        click(loc['x'],loc['y'])
                        page.keyboard.press('Enter')
                        for _ in range(100):
                            if held: break
                            page.wait_for_timeout(100)
                        assert held
                        before_refresh = page.request.get(url+'/progress/me',headers=b_headers).json()['data']
                        page.reload(wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true',timeout=120000)
                        for route, response in held:
                            try: route.fulfill(response=response)
                            except Exception: pass
                        page.wait_for_timeout(1200)
                        click(500,280)
                        type_credentials(account_b['username'])
                        click(500,355)
                        type_credentials(account_b['password'])
                        with page.expect_response(lambda r:r.url.endswith('/auth/login')) as relogin_b:
                            click(500,432)
                        assert relogin_b.value.status == 200
                        page.wait_for_function("JSON.parse(window.task5UiState || '{}').scene === 'map'")
                        after_refresh = page.request.get(url+'/progress/me',headers=b_headers).json()['data']
                        assert after_refresh == before_refresh
                        assert json.loads(page.evaluate('window.task5UiState'))['score'] == before_refresh['score']
                        assert not errors, errors
                        assert '/quiz/start' in [item['path'] for item in diagnostic['network']]
                        assert diagnostic.get('session_submissions', [False])[0], 'Quiz đầu phải dùng phiên server'
                        result = {'ui_login': True, 'qQ_credentials_tab_backspace_enter': True, 'notebook_read_only': True,
                                  'ui_investigation': True, 'ui_quiz_wrong_correct': True,
                                  'ui_review': True, 'ui_quest_confirmed': True,
                                  'ui_leaderboard': True, 'next_location_input_sent': True,
                                  'timeline_canvas':timeline_results,
                                  'canvas_account_isolation_progress_save': True,
                                  'canvas_refresh_progress_save_after_commit': True,
                                  'hud_evidence': hud_evidence,
                                  'not_tested': ['account isolation executed separately via TASK5_ISOLATION_ENDPOINT',
                                      'refresh inside backend transaction',
                                      'HUD other scenes and queued/pending/failed/reconciling'],
                                  'page_errors': errors, 'http_mock': False,
                                  'scope': 'Quest đầu; nhập chuyển địa điểm thứ hai; API/SQLite thật.'}
                        (root / 'data/sqlite-ui-result.json').write_text(
                            json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
                        print(json.dumps(result, ensure_ascii=True))
                        return 0
                    except Exception:
                        diagnostic['ui_state'] = page.evaluate('window.task5UiState || null')
                        diagnostic['focus'] = page.evaluate('document.activeElement.tagName')
                        page.screenshot(path=str(root / 'data/sqlite-ui-timeout.png'))
                        # Chỉ các trường allowlist; không capture headers, body, browser trace.
                        text = json.dumps(diagnostic, ensure_ascii=True, indent=2)
                        text = text.replace(password, '[REDACTED]').replace(username, '[REDACTED]')
                        (root / 'data/sqlite-ui-diagnostic.json').write_text(text, encoding='utf-8')
                        print('UI_SAFE_DIAGNOSTIC=' + text, flush=True)
                        if os.getenv('GITHUB_ACTIONS') == 'true':
                            summary = json.dumps({k: diagnostic.get(k) for k in
                                ('credentials_received', 'ui_state', 'focus', 'network', 'clicks')}, ensure_ascii=True)
                            print('::error title=Auth safe state::' + summary.replace('%', '%25'), flush=True)
                        raise
                    finally:
                        browser.close()
            finally:
                server.terminate()
                server.wait(timeout=15)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        if os.getenv('GITHUB_ACTIONS') == 'true':
            # Chỉ traceback, không local variables/token/password; annotation đọc được ở trang run.
            import traceback
            diagnostic = traceback.format_exc().replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
            print('::error title=SQLite UI diagnostic::' + diagnostic, flush=True)
        raise