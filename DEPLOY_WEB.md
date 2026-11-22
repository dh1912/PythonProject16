# Chạy lại nghiệm thu canvas có điều khiển

Sau build sạch, chạy từng endpoint với biến môi trường:
`TASK5_ISOLATION_ENDPOINT=/quiz/submit python -m task5.check_sqlite_ui`.
Lặp với `/clues/collect`, `/quest/complete`, `/review/retry`.
Thêm `TASK5_REFRESH_AFTER_COMMIT=1` để kiểm thử reload sau COMMIT thực.
PowerShell dùng `$env:TASK5_ISOLATION_ENDPOINT='/quiz/submit'` trước lệnh Python.
Harness tạo tài khoản/SQLite tạm; không trỏ vào DB staging/người chơi.

Tám ca đã đạt Edge, chưa có kết quả Chromium Linux cho code mới. Không dùng kết quả
này để bỏ qua ma trận HUD hoặc refresh trước/trong commit. Staging còn bị chặn bởi
các bằng chứng này và CI mới; không tự deploy, không thay đổi yêu cầu HTTPS,
volume /data/game.db, một worker/replica và secret ổn định đã nêu dưới đây.

# Phạm vi nghiệm thu UI bổ sung

Edge canvas đã kiểm tra logout A/login B trong lúc giữ response save đã commit,
và refresh sau commit save. Map/confirmed rõ ở 1280×900, 1366×768, 1920×1080.
Không dùng các kết quả này thay cho pending quiz/clue/review/quest hoặc toàn ma trận
HUD. Chưa đủ tiêu chí Final P1 để gán READY FOR CONTROLLED STAGING.
Run GitHub 44989309207 và CI/Docker cho code mới chưa xác minh trong lượt này.
Không deploy staging trước khi người dùng cấp cấu hình hosting/quyền hợp lệ.

# Bổ sung hardening: staging giới hạn truy cập

Chưa triển khai HTTPS trong lượt nghiệm thu này. Trước khi cấp quyền staging:

1. Đặt reverse proxy HTTPS có SSO/VPN hoặc danh sách IP được phép ở trước **toàn bộ**
   web và API; không chỉ bảo vệ trang gốc. Không mở trực tiếp cổng Uvicorn ra Internet.
2. Một replica, một worker; mount `/data`, đặt `SQLITE_DB_PATH=/data/game.db`.
   Giữ `JWT_SECRET` ổn định bằng secret của hosting, không ghi vào Docker image.
3. Kiểm tra `/api/health`, dung lượng volume và log lỗi `SQLITE_BUSY`, `disk full`,
   lỗi I/O hằng ngày. Cảnh báo khi dung lượng trống thấp; không xóa WAL thủ công.
4. Backup bằng `sqlite3.Connection.backup()` sang file ngoài static. Mở bản backup
   bằng connection riêng, chạy `PRAGMA integrity_check` và `PRAGMA foreign_key_check`.
   Sao lưu trước mỗi migration; kiểm tra phục hồi trên đường dẫn DB tạm trước.
5. Restore/rollback: chặn ghi và dừng backend trước, giữ bản DB lỗi để điều tra,
   phục hồi backup đã kiểm tra cùng image tương ứng; không ghép DB cũ với WAL mới.
   Sau khởi động kiểm tra health, đăng nhập thử và đối chiếu điểm/tiến độ đã ghi nhận.
6. Không dùng kết quả tải bốn tài khoản dưới đây làm cam kết năng lực production.

Lệnh đo tải độc lập (DB tạm, không thay cấu hình dữ liệu người chơi):
`python -m task5.check_sqlite_load`.

Kiểm thử logout/đổi tài khoản khi request đang pending bằng **canvas thật** và HUD
25 tổ hợp scene/trạng thái ở ba viewport vẫn chưa nghiệm thu; chưa cấp staging
không giới hạn chỉ dựa vào unit test generation guard.

# Deploy FastAPI + Pygbag + SQLite

## Checklist staging HTTPS và rollback
Không phát hành trong lượt nghiệm thu. Hosting phải có TLS proxy, persistent disk local
mount `/data`, một replica và một worker. Đặt SQLITE_DB_PATH=/data/game.db,
JWT_SECRET cố định trong secret store, PORT do hosting cấp, ALLOWED_ORIGINS đúng URL HTTPS.
Không đặt DB/backup dưới WEB_BUILD_DIR; không dùng disk NFS với WAL.
1. Ghi lại image digest/commit đang chạy; backup bằng SQLite Backup API trước upgrade.
2. Kiểm backup bằng `sqlite3.connect(path).execute('PRAGMA integrity_check')` và foreign_key_check.
3. Khởi động image mới, kiểm /api/health, login thử, điểm/clue/review và restart volume.
4. Nếu migration thất bại: dừng container, giữ DB lỗi cùng WAL/SHM để phân tích, phục hồi
   backup vào volume riêng sạch; chạy image cũ khớp schema backup. Không downgrade schema
   bằng cách sửa user_version hoặc ghi backup đè khi backend còn hoạt động.
5. Xác minh login/điểm/completed sau restore rồi mới cho người dùng staging truy cập.
Session cleanup lazy chạy khi start: tối đa 100 hàng/lần, chỉ expiry quá 7 ngày;
answer_log/review/progress vẫn giữ. Không coi session table là audit mọi lần thử vĩnh viễn.

## Giao thức timed quiz P1 (migration 007)
Khi hiển thị câu, POST /quiz/start {ma_cau_hoi}; giữ session_id rồi POST /quiz/submit
{ma_cau_hoi,session_id,dap_an_chon}. Server tính elapsed từ timestamp SQLite; token có
hạn 1 giờ và gắn user/question. Start trùng không reset đồng hồ, tối đa 12 phiên mở.
Không session: tương thích cũ chỉ base/streak, không thưởng tốc độ từ so_giay client.
Mất response: GET /progress/me để đối soát; replay cùng token/lựa chọn không thưởng lặp.
Backup trước migration 007 được tạo tự động; giữ một worker/replica và đồng hồ host UTC
ổn định. Phiên hết hạn cần thử mở lại; chưa có cleanup định kỳ session đã hoàn tất.
Chưa nghiệm thu browser fault matrix toàn bộ/timeline UI mới; không dùng cho kỳ thi có giá trị.

## Release-readiness và giới hạn staging
Nhánh improve/task5-release-readiness lọc đáp án ở HTTP và gói WASM; online chấm server.
Không dùng build trước bản sửa này để nghiệm thu bảo mật. Save chỉ confirmed sau khi đọc
server, timeout cần đọc lại tiến độ trước thử lại; không tự cộng điểm tại client.
Chưa có question-session server: so_giay client gửi vẫn gian lận được. Không dùng bảng vàng
cho kỳ thi/chấm thưởng có giá trị trước khi giải quyết thời gian và test fault mạng còn thiếu.

SQLite chỉ có một writer: BEGIN IMMEDIATE + busy_timeout không làm tăng số writer.
Giữ một replica/worker, disk local bền vững, không NFS; 503/busy phải hiển thị lỗi và retry
có idempotency. Không scale nhiều container chung file để xử lý tải.
Backup vận hành: `python -c "from pathlib import Path; from data.sqlite_store import backup_database; backup_database(Path('/backups/game.sqlite'))"`.
Đặt backup ngoài static, quyền truy cập riêng. Test WAL restore kiểm integrity và giữ điểm/_task5
đã có trong tests/test_release_security.py. Restore thực: dừng backend, giữ bản DB cũ,
đảm bảo không dùng WAL/SHM cũ cạnh DB thay thế; khởi động bằng volume đã phục hồi và kiểm health/login.
JWT_SECRET ổn định, HTTPS và kiểm thử tải/fault vẫn là điều kiện staging có kiểm soát.

## Nghiệm thu Linux mới nhất
Run https://github.com/dh1912/PythonProject16/actions/runs/44913145381 tại f4a255f
SUCCESS: pytest, compile, Pygbag, Chromium UI SQLite thật, Docker build và restart
persistent volume. Lỗi chữ hoa SDL web đã sửa bằng TEXTINPUT và harness phím Shift.
Các ghi chú FAIL cũ phía dưới chỉ là lịch sử; chưa tự triển khai public.
UI-state chẩn đoán chỉ bật với `/web/?acceptance=1`, không trả nội dung thông tin đăng nhập.

### Kết quả hosting prerequisite thực tế
Run 44911172510 (ea8d86f) đã SUCCESS Docker build và container SQLite persistent-volume
qua restart: tài khoản/điểm/manh mối/completed khôi phục nguyên vẹn. Tuy nhiên workflow
tổng thể FAIL vì Chromium Linux UI timeout lúc login. Edge Windows cùng code HEAD đạt.
Chưa deploy public; không dùng kết quả Docker để bỏ qua lỗi UI Linux chưa nghiệm thu.

## Mốc Git được nghiệm thu độc lập
Commit chức năng `faeb1e2` đã chạy từ detached worktree và venv mới: 81 pytest + 7
subtest, compile, build Pygbag, Edge UI tài khoản chứa q/Q và toàn tuyến API 9 quest đạt.
Nhánh fix/sqlite-web-deploy đã push; workflow thật xem tại
https://github.com/dh1912/PythonProject16/actions/runs/44910700587 .
Chỉ kết luận Docker/persistent disk PASS sau khi step container trong run này thành công;
local Windows vẫn không có Docker. Push nhánh không phải triển khai public.

## CI Linux và nghiệm thu trước phát hành
Workflow `.github/workflows/sqlite-web.yml` chạy Python 3.11, pytest (SQLite file tạm),
compile, Pygbag, Chromium UI thật, build Docker và chạy container với volume `/data`.
Helper `python -m task5.ci_container_check create --state <file-tạm>` đăng ký tài khoản
ngẫu nhiên, chấm quiz/lưu clue/quest; sau restart, chế độ `restore` kiểm tra toàn bộ tiến độ.
File trạng thái chứa tài khoản thử chỉ đặt tại RUNNER_TEMP, không upload artifact và được xóa.
Chưa push workflow/chưa chạy Docker tại máy phát triển: chưa có kết quả CI/Docker thật.
Chỉ push nhánh/trigger workflow sau khi các thay đổi v6 phụ thuộc đã được review và commit;
không merge main hoặc deploy public tự động.

Chạy UI local sau build: `python -m task5.check_sqlite_ui` (Windows dùng Edge;
Linux cần `python -m playwright install --with-deps chromium`). Cần cài `playwright`.

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
Lần đầu tự tạo schema và seed nội dung từ `historical_seed.json`; migration 006 bổ sung
đúng các dòng được thay thế trong `004_task4_complete.sql` từ `historical_v6.json`.
Không seed user. Migration ghi manifest ổn định để chạy lại không tạo bản sao; bản ghi
legacy không bị xóa, chỉ các hàng manifest được chọn làm nội dung active tại bốn sự kiện
Task 4. ID lịch sử được giữ ổn định qua `content_manifest`.
DB cũ được backup bằng SQLite backup API trước nâng phiên bản, tên `*.backup-UTC`.
Không xóa bảng Task khác. Nếu dữ liệu cũ trùng user progress, migration dừng để xử lý
thủ công thay vì xóa dữ liệu. Backup vận hành dùng sqlite3.Connection.backup(),
không chỉ copy game.db khi WAL đang hoạt động. Restore: dừng backend, giữ bản cũ,
thay bằng backup đã kiểm integrity_check, khởi động lại và kiểm login/điểm.
Tài khoản legacy plaintext phải đặt lại mật khẩu an toàn, không bỏ qua hash.

Docker chỉ được ghi PASS khi đã build/run/restart volume thật. Không có Docker:
ghi CHƯA KIỂM THỬ. Không merge main hoặc push tự động.