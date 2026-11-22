"""Đo tải HTTP thật trên FastAPI/SQLite tạm; không tắt rate limit hoặc dùng DB thật."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
import argparse
import os
from pathlib import Path
import secrets
import socket
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accounts', type=int, choices=(4,8,16), default=4)
    count = parser.parse_args().accounts
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='task5-load-') as directory:
        db = Path(directory) / 'load.db'
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        env = dict(os.environ, SQLITE_DB_PATH=str(db),
                   JWT_SECRET=secrets.token_urlsafe(48), PYTHONUTF8='1')
        measurements: list[dict] = []

        def call(path: str, payload=None, token=None, measured=True):
            headers = {'Content-Type': 'application/json'}
            if token:
                headers['Authorization'] = 'Bearer ' + token
            request = Request(base + path, headers=headers,
                              data=None if payload is None else json.dumps(payload).encode())
            started = time.perf_counter()
            try:
                response = urlopen(request, timeout=30)
            except HTTPError as exc:
                response = exc
            with response:
                body = json.load(response)
                status = response.status
            if measured:
                # Không lưu body, tài khoản, token hoặc headers vào artifact.
                measurements.append({'path': path, 'status': status,
                                     'ms': round((time.perf_counter()-started)*1000, 2)})
            assert 200 <= status < 300, f'{path}: HTTP {status}'
            return body

        with (Path(directory)/'server.log').open('w', encoding='utf-8') as log:
            server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'task5.server.app:app',
                                       '--host', '127.0.0.1', '--port', str(port)],
                                      cwd=root, env=env, stdout=log, stderr=log)
            try:
                for _ in range(100):
                    try:
                        call('/api/health', measured=False)
                        break
                    except OSError:
                        time.sleep(.2)
                else:
                    raise RuntimeError('API tải chưa sẵn sàng')
                content = call('/game/content', measured=False)
                loc = content['locations'][0]
                clues = content['investigation_data'][loc['name']]['clues']
                with closing(sqlite3.connect(db)) as conn:
                    qid, answer = conn.execute('SELECT ma_cau_hoi,dap_an_dung FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 1').fetchone()
                answer = ord(answer)-65
                # Đăng nhập theo quota cùng IP; tải gameplay sau đó chạy đồng thời.
                # Không tắt limiter, không giả IP hay sửa cấu hình bảo mật server.
                credentials = [{'username': 'load_'+secrets.token_hex(6),
                                'password': secrets.token_urlsafe(18)} for _ in range(count)]
                for account in credentials:
                    call('/auth/register', {**account, 'fullname': 'Tài khoản tải tạm'}, measured=False)

                tokens = []
                for index, account in enumerate(credentials):
                    if index and index % 5 == 0:
                        time.sleep(61)
                    tokens.append(call('/auth/login', account)['access_token'])
                # Quota quiz 30/phút/IP: 16 người * 3 submits cần chia hai đợt.
                # Đo contention từng đợt, không giả định 16 submits đồng thời được phép.
                def player(token):
                    session = call('/quiz/start', {'ma_cau_hoi': str(qid)}, token)['session_id']
                    wrong = {'ma_cau_hoi': str(qid), 'session_id': session, 'dap_an_chon': (answer+1)%4}
                    assert not call('/quiz/submit', wrong, token)['correct']
                    retry = {'ma_cau_hoi': str(qid), 'dap_an_chon': answer}
                    # Hai retry thực đồng thời, chỉ một transaction được thưởng.
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        results = list(pool.map(lambda _: call('/review/retry', retry, token), range(2)))
                    assert sum(r['points_awarded'] for r in results) == 15
                    session = call('/quiz/start', {'ma_cau_hoi': str(qid)}, token)['session_id']
                    payload = {'ma_cau_hoi': str(qid), 'session_id': session, 'dap_an_chon': answer}
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        results = list(pool.map(lambda _: call('/quiz/submit', payload, token), range(2)))
                    assert sum(r['points_awarded'] > 0 for r in results) == 1
                    for clue in clues:
                        call('/clues/collect', {'ma_dia_diem': loc['id'], 'ma_manh_moi': str(clue['id']),
                                               'tu_lieu_chon': clue['name']}, token)
                    quest = {'ma_dia_diem': loc['id'], 'ten_dia_diem': loc['name'], 'nam_mo_khoa': 1914}
                    assert call('/quest/complete', quest, token)['bonus'] == 30
                    assert call('/quest/complete', quest, token)['bonus'] == 0
                    call('/progress/save', {'current_loc_id':loc['id'],'max_year':1914,
                                           'completed':[],'task4':{}}, token)
                    progress = call('/progress/me', token=token)['data']
                    assert loc['name'] in progress['completed']
                    return progress['score']

                started = time.perf_counter()
                scores = []
                for offset in range(0,count,8):
                    if offset:
                        time.sleep(61)
                    with ThreadPoolExecutor(max_workers=min(count,8)) as pool:
                        scores.extend(pool.map(player, tokens[offset:offset+8]))
                with closing(sqlite3.connect(db)) as conn:
                    assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
                    assert not conn.execute('PRAGMA foreign_key_check').fetchall()
                times = sorted(row['ms'] for row in measurements)
                result = {'accounts': count, 'concurrent_players':min(count,8),
                          'peak_workers': min(count,8)*2, 'requests': len(times),
                          'success': len(times), 'failed': 0, 'sqlite_busy_http_503': 0,
                          'elapsed_seconds': round(time.perf_counter()-started, 3),
                          'median_ms': statistics.median(times),
                          'p95_ms': times[min(len(times)-1, int(len(times)*.95))],
                          'max_ms': max(times), 'all_scores_nonnegative': all(s >= 0 for s in scores),
                          'scope': 'HTTP thật; login theo quota, gameplay tối đa 8 người/đợt; không phải production benchmark',
                          'measurements': measurements}
                (root/f'data/sqlite-load-{count}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
                print(json.dumps({k: v for k, v in result.items() if k != 'measurements'}, ensure_ascii=True))
                return 0
            finally:
                server.terminate()
                server.wait(timeout=20)


if __name__ == '__main__':
    raise SystemExit(main())