"""Chạy browser thật để kiểm tra frame đầu; không dùng kết nối DB.

Yêu cầu playwright và Microsoft Edge. Chỉ kiểm tra render, không thay thế E2E
đăng nhập/quiz/lưu tiến độ. Kết quả và ảnh được lưu dưới data/.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
import urllib.request


def main() -> int:
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--mock-login", action="store_true", help="Kiểm tra UI login/fetch với HTTP giả, không dùng DB.")
    parser.add_argument("--mock-actions", action="store_true", help="Kiểm tra thêm retry và Bảng Vàng với HTTP giả.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = root / "build" / "web-source" / "build" / "web"
    if not (build / "index.html").is_file():
        raise FileNotFoundError("Chạy python -m task5.build_web trước.")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env.update(WEB_BUILD_DIR=str(build), DB_NAME="game_dev", DB_USER="acceptance_disabled",
               DB_PASSWORD="not-a-real-password", JWT_SECRET=secrets.token_urlsafe(48), PYTHONUTF8="1")
    messages = []
    data = root / "data"
    data.mkdir(exist_ok=True)
    with (data / "browser-check-server.log").open("w", encoding="utf-8") as stream:
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "task5.server.app:app", "--host", "127.0.0.1", "--port", str(port)], cwd=root, env=env, stdout=stream, stderr=stream)
        try:
            url = f"http://127.0.0.1:{port}"
            for _ in range(40):
                try:
                    with urllib.request.urlopen(url + "/api/health", timeout=1):
                        break
                except OSError:
                    time.sleep(0.25)
            else:
                raise RuntimeError("Server kiểm tra không khởi động.")
            with sync_playwright() as browser_api:
                browser = browser_api.chromium.launch(channel="msedge", headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 800})
                    auth_requests = []
                    if args.mock_login or args.mock_actions:
                        def login_response(route):
                            auth_requests.append("login")
                            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                                "access_token": "browser-test-token", "user": {"ma_nguoi_dung": 123, "ho_va_ten": "Browser Test"},
                                "progress": {"score": 30, "current_loc_id": 1, "max_year": 1914, "completed": [], "task4": {}}}))
                        def review_response(route):
                            auth_requests.append("review")
                            items = [{"id": "task4:test", "location_name": "Test", "question": "Choose B", "options": ["A", "B"], "correct_index": 1, "user_choice": 0, "status": "PENDING"}] if args.mock_actions else []
                            route.fulfill(status=200, content_type="application/json", body=json.dumps({"items": items}))
                        page.route("**/auth/login", login_response)
                        # Không để browser test vô tình gọi DB qua endpoint nội dung.
                        page.route("**/game/questions", lambda route: route.fulfill(
                            status=200, content_type="application/json", body='{"questions":{}}'))
                        page.route("**/review/me", review_response)
                        def retry_response(route):
                            auth_requests.append("retry")
                            route.fulfill(status=200, content_type="application/json", body='{"is_correct":true,"points_awarded":15,"total_score":45}')
                        def leaderboard_response(route):
                            auth_requests.append("leaderboard")
                            route.fulfill(status=200, content_type="application/json", body='{"leaderboard":[{"display_name":"Browser Test","score":45}]}')
                        page.route("**/review/retry", retry_response)
                        page.route("**/leaderboard", leaderboard_response)
                    page.on("console", lambda msg: messages.append({"type": msg.type, "text": msg.text}))
                    page.on("pageerror", lambda exc: messages.append({"type": "pageerror", "text": str(exc)}))
                    page.goto(url + "/web/", wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(args.seconds * 1000)
                    if args.mock_login or args.mock_actions:
                        canvas = page.locator("#canvas")
                        box = canvas.bounding_box()
                        width, height = canvas.evaluate("c=>[c.width,c.height]")
                        scale = min(width/1280, height/720)
                        ox, oy = (width-1280*scale)/2, (height-720*scale)/2
                        def click(x, y):
                            canvas.click(position={"x": (ox+x*scale)*box["width"]/width,
                                                   "y": (oy+y*scale)*box["height"]/height})
                        click(500, 280)
                        page.keyboard.type("student", delay=100)
                        click(500, 355)
                        page.keyboard.type("test-password", delay=100)
                        click(500, 432)
                        page.wait_for_timeout(5000)
                        if args.mock_actions:
                            page.keyboard.press("r")
                            page.wait_for_timeout(1000)
                            page.keyboard.press("2")
                            page.wait_for_timeout(2000)
                            page.keyboard.press("Escape")
                            page.wait_for_timeout(1000)
                            page.keyboard.press("b")
                            page.wait_for_timeout(2000)
                    page.screenshot(path=str(data / "browser-check.png"))
                    # Chứng minh Game đã chạy, không chỉ có canvas loader dựng sẵn.
                    ready = page.evaluate("Boolean(window.task5GameReady)")
                    errors = [m for m in messages if m["type"] == "pageerror"]
                    result = {"first_frame_ready": ready, "page_errors": errors, "messages": messages,
                              "auth_requests": auth_requests,
                              "scope": "First-frame và tùy chọn UI login/fetch giả; không chứng minh DB."}
                    (data / "browser-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    expected = ["login", "review", "retry", "leaderboard"] if args.mock_actions else ["login", "review"]
                    login_ok = not (args.mock_login or args.mock_actions) or auth_requests == expected
                    print(json.dumps({"first_frame_ready": ready, "mock_login_pass": login_ok, "page_errors": errors}))
                    return 0 if ready and login_ok and not errors else 1
                finally:
                    browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())