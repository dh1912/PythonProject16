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
                    page.on("console", lambda msg: messages.append({"type": msg.type, "text": msg.text}))
                    page.on("pageerror", lambda exc: messages.append({"type": "pageerror", "text": str(exc)}))
                    page.goto(url + "/web/", wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(args.seconds * 1000)
                    page.screenshot(path=str(data / "browser-check.png"))
                    # Chứng minh Game đã chạy, không chỉ có canvas loader dựng sẵn.
                    ready = page.evaluate("Boolean(window.task5GameReady)")
                    errors = [m for m in messages if m["type"] == "pageerror"]
                    result = {"first_frame_ready": ready, "page_errors": errors, "messages": messages,
                              "scope": "Chỉ first-frame; không chứng minh auth, quiz hoặc DB."}
                    (data / "browser-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(json.dumps({"first_frame_ready": ready, "page_errors": errors}))
                    return 0 if ready and not errors else 1
                finally:
                    browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())