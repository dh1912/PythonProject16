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
        # Log nằm ngoài DB tạm: Windows/antivirus có thể giữ handle sau terminate.
        with (root / 'data/sqlite-ui-server.log').open('w', encoding='utf-8') as log:
            server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'task5.server.app:app',
                                       '--host', '127.0.0.1', '--port', str(port)],
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
                        paths: list[str] = []
                        page.on('pageerror', lambda exc: errors.append(str(exc)))
                        page.on('response', lambda response: paths.append(response.url.split(url)[-1])
                                if response.ok and response.url.startswith(url) else None)
                        username = 'ui_qQ_' + secrets.token_hex(5)
                        password = 'ui-qQ-test-password-' + secrets.token_hex(5)
                        registration = page.request.post(url + '/auth/register', data={
                            'username': username, 'password': password, 'fullname': 'UI Acceptance'})
                        assert registration.status == 201
                        headers = {'Authorization': 'Bearer ' + registration.json()['access_token']}
                        content = page.request.get(url + '/game/content').json()
                        loc = next(item for item in content['locations'] if item['id'] == 1)
                        page.goto(url + '/web/', wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true', timeout=120000)
                        page.wait_for_timeout(1500)
                        canvas = page.locator('#canvas')

                        def click(x: float, y: float) -> None:
                            page.wait_for_function("document.querySelector('#canvas').width > 0 && document.querySelector('#canvas').height > 0", timeout=15000)
                            box = canvas.bounding_box()
                            assert box
                            w, h = canvas.evaluate('c=>[c.width,c.height]')
                            scale = min(w / 1080, h / 720)
                            canvas.click(position={
                                'x': ((w - 1080 * scale) / 2 + x * scale) * box['width'] / w,
                                'y': ((h - 720 * scale) / 2 + y * scale) * box['height'] / h})

                        def progress() -> dict:
                            response = page.request.get(url + '/progress/me', headers=headers)
                            assert response.ok
                            return response.json()['data']

                        # Chỉ tạo fixture bằng HTTP; toàn bộ hành động chơi dưới đây qua UI.
                        click(500, 280)
                        page.keyboard.type(username, delay=40)
                        if sys.platform == 'win32':
                            page.keyboard.press('Tab')
                        else:
                            click(500, 355)
                        page.keyboard.type(password, delay=40)
                        page.keyboard.type('x')
                        page.keyboard.press('Backspace')
                        with page.expect_response(lambda r: r.url.endswith('/review/me') and r.ok):
                            if sys.platform == 'win32':
                                page.keyboard.press('Enter')
                            else:
                                click(500, 432)
                        page.wait_for_timeout(1500)
                        before = progress()
                        page.keyboard.press('n')
                        page.wait_for_timeout(1200)
                        page.screenshot(path=str(root / 'data/sqlite-ui-notebook.png'))
                        assert progress() == before, 'Mở Notebook không được tăng tiến độ/điểm.'
                        page.keyboard.press('Escape')
                        click(loc['x'], loc['y'])
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(800)
                        for index in range(len(content['investigation_data'][loc['name']]['clues'])):
                            page.keyboard.press(str(index + 1))
                            page.wait_for_timeout(200)
                            for choice in ('1', '2', '3'):
                                page.keyboard.press(choice)
                                page.wait_for_timeout(500)
                        page.keyboard.press('d')
                        page.wait_for_timeout(800)
                        questions = content['questions'][loc['name']]
                        q = questions[0]
                        with page.expect_response(lambda r: r.url.endswith('/quiz/submit') and r.ok):
                            page.keyboard.press(str((q['answer'] + 1) % 4 + 1))
                        page.wait_for_timeout(700)
                        # Sai không được hoàn thành quest; thử lại đúng trên cùng câu.
                        assert not progress()['completed']
                        for q in questions:
                            with page.expect_response(lambda r: r.url.endswith('/quiz/submit') and r.ok):
                                page.keyboard.press(str(q['answer'] + 1))
                            page.wait_for_timeout(700)
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
                        assert not errors, errors
                        result = {'ui_login': True, 'qQ_credentials_tab_backspace_enter': True, 'notebook_read_only': True,
                                  'ui_investigation': True, 'ui_quiz_wrong_correct': True,
                                  'ui_review': True, 'ui_quest_confirmed': True,
                                  'ui_leaderboard': True, 'next_location_input_sent': True,
                                  'page_errors': errors, 'http_mock': False,
                                  'scope': 'Quest đầu; nhập chuyển địa điểm thứ hai; API/SQLite thật.'}
                        (root / 'data/sqlite-ui-result.json').write_text(
                            json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
                        print(json.dumps(result, ensure_ascii=True))
                        return 0
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