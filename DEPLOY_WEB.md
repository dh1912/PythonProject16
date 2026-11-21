# Deploy FastAPI + Pygbag + SQLite

Không cần MySQL/XAMPP. Chạy một backend instance với persistent disk local;
không đặt SQLite trên NFS hoặc thư mục static. Không public trước nghiệm thu.

## Local
```powershell
python -m pip install -r requirements-server.txt -r requirements-client.txt
$env:SQLITE_DB_PATH='C:\duong-dan-rieng\game.db'
$env:JWT_SECRET=(python -c "import secrets; print(secrets.token_urlsafe(48))")
python -m task5.build_web
$env:WEB_BUILD_DIR=(Resolve-Path '.\build\web-source\build\web').Path
python -m uvicorn task5.server.app:app --host 127.0.0.1 --port 8000
```
Truy cập `/web/`, `/docs`, `/teacher/login`. `.env` chỉ là mẫu biến môi trường,
không tự nạp nếu không dùng công cụ dotenv. Desktop: `python main.py`.

## Docker/hosting có persistent disk
```sh
docker build -t history-game .
docker volume create history-data
docker run --name history-game -p 8000:8000 --mount source=history-data,target=/data -e JWT_SECRET="$JWT_SECRET" -e ALLOWED_ORIGINS=https://your-host history-game
```
Đặt SQLITE_DB_PATH=/data/game.db, WEB_BUILD_DIR=/app/build/web, PORT theo hosting.
Mount disk vào /data, giữ một replica. Dùng HTTPS của hosting/reverse proxy.
Kiểm `/api/health`, tạo tài khoản thử, lưu tiến độ, restart container rồi login lại.
Không đưa tài khoản thật/DB/secret vào Git hoặc gói WASM.

## Migration/backup
Lần đầu tự tạo schema và seed 5 bảng nội dung từ historical_seed.json; không seed user.
DB cũ được backup bằng SQLite backup API trước nâng phiên bản, tên *.backup-UTC.
Không xóa bảng Task khác. Nếu dữ liệu cũ trùng user progress, migration dừng để xử lý
thủ công thay vì xóa dữ liệu. Backup vận hành dùng sqlite3.Connection.backup(),
không chỉ copy game.db khi WAL đang hoạt động. Restore: dừng backend, giữ bản cũ,
thay bằng backup đã kiểm integrity_check, khởi động lại và kiểm login/điểm.
Tài khoản legacy plaintext phải đặt lại mật khẩu an toàn, không bỏ qua hash.

Docker chỉ được ghi PASS khi đã build/run/restart volume thật. Không có Docker:
ghi CHƯA KIỂM THỬ. Không merge main hoặc push tự động.