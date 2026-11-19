# Task 5 — điểm, ôn tập, lưu tiến độ và triển khai web

## Trạng thái quan trọng

Task 5 đang được bổ sung trong checkout này. API server và migration có mã nguồn; đã compile, nhưng chưa xác minh với MySQL thật. Không chạy migration trên DB dùng chung. Chế độ trình duyệt chưa được nghiệm thu: các scene game hiện dùng `pygame.font.SysFont`, dữ liệu game desktop còn dựa trên module `data.db_queries`, và API client dùng `urllib` đồng bộ. Pygbag yêu cầu game loop async; gọi HTTP đồng bộ sẽ đóng băng khung hình. Vì vậy chưa công bố là bản web chạy được.

## Tạo database phát triển riêng trên XAMPP

1. Khởi động MySQL trong XAMPP, mở phpMyAdmin hoặc MySQL CLI.
2. Tạo database trống `game_dev`; import TOÀN BỘ `game.sql` vào database này, gồm các `ALTER TABLE ... AUTO_INCREMENT` ở cuối dump. Nếu bỏ phần cuối, đăng ký không thể tự tạo ID vì schema ban đầu không khai báo AUTO_INCREMENT. Dump đi kèm có tài khoản/mật khẩu mẫu dạng rõ, chỉ dùng dữ liệu local thử nghiệm.
3. Chạy migration `data/migrations/003_task5.sql` trong `game_dev`.
4. Tạo user riêng, giới hạn chỉ database phát triển:

```sql
CREATE USER 'task5_server'@'localhost' IDENTIFIED BY 'mat-khau-rieng-dai';
GRANT SELECT, INSERT, UPDATE, DELETE ON game_dev.* TO 'task5_server'@'localhost';
FLUSH PRIVILEGES;
```

Database `game_demo` dành cho demo riêng, phải import schema/dữ liệu cần thiết và chạy migration tại đó. Không đổi `DB_NAME` sang DB nhóm/production để thử.

5. Sao chép `.env.example` thành `.env`, điền `DB_PASSWORD`; tạo `JWT_SECRET` ngẫu nhiên dài ít nhất 32 ký tự. Không commit `.env`.

Cloud MySQL/MariaDB: tạo database và user giới hạn quyền tương tự; đặt biến môi trường trên nền tảng deploy. Migration `002_task2_historical_data.sql` có cú pháp MariaDB, vì thế môi trường nên là MySQL 8 hoặc MariaDB tương thích các statement đó và migration 003.

## Cài và chạy desktop

```powershell
$env:PYTHONUTF8='1'
$env:TASK5_SERVER_ENABLED='0'
python -m pip install -r requirements-client.txt
python .\main.py
```

Khi API đã cấu hình/đang chạy và muốn thử adapter: đặt `TASK5_SERVER_ENABLED=1`, `API_URL=http://127.0.0.1:8000`. Khi tắt cờ, game giữ dịch vụ desktop cũ.

## Chạy API (chỉ với DB thử riêng)

```powershell
python -m pip install -r requirements-server.txt
$env:DB_NAME='game_dev'
$env:DB_USER='task5_server'
$env:DB_PASSWORD='mat-khau-rieng'
$env:JWT_SECRET='tao-mot-secret-ngau-nhien-dai-hon-32-ky-tu'
$env:ALLOWED_ORIGINS='http://localhost:8000'
python -m uvicorn task5.server.app:app --host 127.0.0.1 --port 8000
```

Kiểm tra `/api/health` và OpenAPI `/docs`. Các route chính: `POST /auth/register`, `POST /auth/login`, `POST /quiz/submit`, `GET /progress/me`, `POST /progress/save`, `GET /leaderboard`, `/teacher` (giáo viên/quản trị).

## Luật và giới hạn an toàn

- `ScoringEngine` là công thức nguồn chuẩn: đúng cơ bản 30 + thưởng tốc độ, chuỗi tối đa 1.5; sai trừ 10 nhưng không âm. API lưu một hàng/cặp user-question, nên không phạt sai lặp lại; khi sau đó trả lời đúng, server cập nhật hàng log và cấp điểm đúng một lần.
- Thời gian `so_giay` vẫn do client gửi. API từ chối số âm và giá trị dương dưới 0.25 giây, nhưng người dùng có thể giả mạo số giây hợp lệ; không xem đây là chống gian lận hoàn toàn.
- Vai trò đọc từ `nguoi_dung.vai_tro`; token JWT hết hạn sau một giờ. Đăng nhập legacy so khớp mật khẩu hiện có rồi chỉ thêm bcrypt vào bảng mới, không ghi đè cột legacy.
- API không nhận điểm trong `/progress/save`. `answer_log` là nơi duy nhất cấp điểm quiz server-side.
- Bản dump mẫu `game.sql` chứa thông tin đăng nhập yếu/dạng rõ; không đưa dump đó lên public cloud như dữ liệu thật. Đổi hoặc xóa tài khoản mẫu trước triển khai.

## Test

```powershell
$env:PYTHONUTF8='1'
python -m pytest -q tests
```

Các test hiện có trong checkout này mới bao gồm `tests/test_quest_fsm.py`. Test repository/API cần mock DB hoặc database thử `game_dev`; chưa chạy kiểm thử transaction DB thật.

## Build web / Pygbag

Tài liệu Pygbag: https://pygame-web.github.io/wiki/pygbag/ — game loop phải async và nhường event loop bằng `await asyncio.sleep(0)`. Hướng dẫn cũng cảnh báo I/O đồng bộ/operations chuẩn CPython không phù hợp cho browser. Không dùng `urllib.request.urlopen()` đồng bộ trong browser; cần adapter async dựa trên API browser/Pygbag đã được xác minh thực tế.

```powershell
python -m pip install pygbag
# Chỉ build thư mục staging sạch; ví dụ build thử được tạo ở .web-staging.
python -m pygbag --build --disable-sound-format-error .\.web-staging
```

Build directory phụ thuộc phiên bản Pygbag; kiểm tra output để phục vụ đúng thư mục web. Build thử trong `.web-staging/build/web` và local server trả HTTP 200. Bản build gốc quét cả `.venv-python311` (hơn 2.500 file); bản staging sạch giảm còn khoảng 49 file. Đây chỉ xác nhận đóng gói/phục vụ HTML, chưa xác nhận game khởi chạy hoặc API hoạt động trên browser. Trước khi phát hành còn phải dùng HTTP async/browser fetch (client hiện là urllib đồng bộ và các form game gọi API đồng bộ), thay `SysFont` ở `main.py` cùng scene Task 1/2/4, và chạy thử trực tiếp bằng trình duyệt. Không public bản thử này.

## Deploy

Cấu hình cloud: cài requirements server, đặt DB/JWT/origin qua secret variables, build web trước deploy rồi đặt `WEB_BUILD_DIR` trỏ tới thư mục build đã kiểm tra. FastAPI mount game dưới `/web/`; `/` chuyển tới `/web/` khi build có sẵn, nếu chưa thì hiện trang hướng dẫn và API vẫn ở các route `/api`. HTTPS bắt buộc; dùng reverse proxy/HTTPS của cloud, không mở cổng DB công khai. Kiểm tra endpoint health sau deploy.

## Ảnh báo cáo

Chụp ảnh thật từ ứng dụng, không dựng ảnh giả: (1) bản đồ và hồ sơ người chơi; (2) câu trả lời sai được thêm vào Phòng Ôn tập; (3) thử lại đúng và trạng thái thành thạo; (4) tổng kết số câu sai/thành thạo, điểm/hạng; (5) Bảng Vàng top 10; (6) trang `/teacher` bằng tài khoản giáo viên. Che thông tin cá nhân, token và mật khẩu trong ảnh.

## Câu hỏi giảng viên thường gặp

1. Điểm quiz được tính ở đâu? — API gọi `ScoringEngine`, không lấy điểm từ payload lưu tiến độ.
2. Vì sao dùng `answer_log`? — Ghi dấu một lần theo unique `(ma_nguoi_dung, ma_cau_hoi)` để chống cộng lặp.
3. Có thể gửi điểm giả không? — `/progress/save` không có trường điểm; điểm chỉ cập nhật từ chấm đáp án/quest server.
4. Làm sao lưu mật khẩu? — bcrypt trong `tai_khoan_bao_mat`; tài khoản cũ được migrate khi đăng nhập.
5. JWT chứa gì? — ID người dùng, vai trò chuẩn hóa, thời điểm phát hành/hết hạn; quyền hiện thời vẫn đọc lại DB.
6. Người chơi có xem báo cáo giáo viên không? — Không, dependency yêu cầu vai trò giáo viên/quản trị.
7. Có chống gian lận thời gian tuyệt đối không? — Không; thời gian client vẫn giả được, chỉ chặn giá trị cực nhỏ/âm.
8. Tại sao không dùng SQLAlchemy? — Yêu cầu dự án dùng PyMySQL và helper DB hiện có.
9. Có sửa bảng cũ không? — Migration 003 chỉ `CREATE TABLE IF NOT EXISTS` ba bảng mới.
10. Web đã được nghiệm thu chưa? — Chưa; phải thay I/O đồng bộ, thread và font hệ thống bằng phương án browser-compatible rồi chạy Pygbag thật.