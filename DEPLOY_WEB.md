# Deploy web (nhánh tích hợp)
Dùng MariaDB, FastAPI và Pygbag cùng origin. Không dùng SQLite cho backend.
## Database mới, riêng biệt
Tạo database trống game_demo bằng tài khoản quản trị. Import theo thứ tự:
1. data/schema_seed.sql
2. data/migrations/003_task5.sql
3. data/migrations/004_task4_complete.sql: chỉ trên DB trống vừa seed, bỏ dòng USE game để không ghi nhầm database; migration xóa và tạo lại câu hỏi/manh mối nên không áp dụng lên DB có tiến độ.
Tạo user ứng dụng giới hạn SELECT, INSERT, UPDATE, DELETE trên game_demo. Không dùng tài khoản root. Không đưa dữ liệu tài khoản cũ lên web.
## Docker
docker build -t history-game .
Thiết lập biến môi trường DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, JWT_SECRET (ngẫu nhiên tối thiểu 32 ký tự), ALLOWED_ORIGINS và PORT nếu cần. DB_HOST phải truy cập được từ container, không dùng localhost nếu DB ở ngoài container.
docker run --rm -p 8000:8000 --env-file .env history-game
Mở http://localhost:8000/ và /docs. Dùng HTTPS khi public. Có thể deploy Dockerfile trên dịch vụ container với MariaDB bên ngoài.
## Nghiệm thu trước khi merge/public
- Chạy pytest và build Docker.
- Browser thật: đăng ký, sai mật khẩu phải bị chặn, quiz sai, retry, leaderboard, quest, logout/login và lưu tiến độ trên DB riêng.
- Kiểm tra quest chỉ hoàn thành sau phản hồi server, toàn bộ manh mối/câu hỏi có ID khớp.
- Font Arial cần quyền phân phối hoặc thay bằng font mở có hỗ trợ tiếng Việt.
- Chưa xác nhận Docker, DB thật hoặc browser E2E cho lần sửa này.
- Không áp dụng migration vào DB chung/production khi chưa sao lưu và kiểm tra.
