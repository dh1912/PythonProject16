# Biên bản nghiệm thu Task 5 trên workspace hiện tại

## Cập nhật sau kiểm tra browser thật

### Cập nhật transport đăng nhập browser

- Đăng nhập/đăng ký trong LoginScene đã chọn coroutine fetch khi chạy Emscripten; game loop poll kết quả, không chặn vẽ.
- Cache review/progress được nạp qua fetch trước khi áp dụng phiên, tránh gọi urllib đồng bộ trong apply_user_session.
- Sửa scale/render và click theo kích thước Surface SDL thực, không kích thước cửa sổ yêu cầu bị browser ép.
- Edge headless đã thao tác bàn phím/chuột bình thường, gửi `/auth/login` và `/review/me` qua fetch (HTTP response giả), vào bản đồ với người chơi Browser Test, điểm 30; không có pageerror. Ảnh `data/browser-auth.png`, kết quả `data/browser-auth-result.json`.
- Đây là E2E UI + browser transport với HTTP giả, không phải chứng nhận đăng nhập MySQL thật.
- Các thao tác quiz/retry/save/leaderboard browser còn dùng call-site đồng bộ; chưa nghiệm thu chúng.

- Đã cài Playwright và sử dụng Microsoft Edge headless có sẵn trên máy.
- `python -m task5.check_web_runtime --seconds 65`: mã thoát 0, `first_frame_ready=true`, `page_errors=[]`.
- Dấu ready chỉ đặt sau khi `Game.step()` đã chạy một frame; không dựa vào HTTP 200 hay sự tồn tại của canvas loader.
- Kết quả máy đọc được tại `data/browser-check.json`, ảnh thật `data/browser-check.png`.
- Tổng test mới: 36 test chính và 7 subtest đạt. Build sạch mã thoát 0.
- Đã thêm BrowserApiClient async dựa trên fetch/platform.jsiter, có timeout/HTTP-error; test giải mã đạt. **Chưa nối transport này vào tất cả event handler đồng bộ của Game**, nên không xác nhận auth/quiz/save browser E2E.
- Phạm vi đạt mới: browser khởi tạo và render frame game đầu. Không đồng nghĩa đủ phiên chơi, login/DB, hoặc deploy công khai.

## Kết quả chạy trong lượt nghiệm thu

- `python -m pytest -q tests`: 32 test chính đạt, 7 subtest đạt, 1 cảnh báo Starlette TestClient deprecation.
- `python -m compileall -q task5 tests main.py main_web.py scenes/review_scene.py`: mã thoát 0.
- Smoke desktop dùng cache, chặn kết nối DB: Game khởi tạo/vẽ login và phòng ôn tập thành công.
- `python -m task5.build_web`: mã thoát 0; build tại `build/web-source/build/web`.
- Kiểm tra ZIP/APK: có `assets/game_desktop.py`, entry point chọn đúng module; không chứa `.env`, profile reviews hoặc thư mục server.
- HTML build không còn thẻ script BrowserFS 0.9.3 trỏ URL 404.

## Các mục đạt trong phạm vi đã kiểm thử

| Mục | Bằng chứng | Phạm vi |
|---|---|---|
| Điểm/hạng cơ bản, phạt một lần trong phiên | test_task5_local.py | Unit |
| Cách ly kho JSON, dấu thưởng sau reload, không ghi JSON API profile | test_task5_local.py | Unit, file tạm |
| Chuỗi đúng server, duplicate không cộng, rollback quest ID giả, chặn khóa nội bộ | test_task5_repository.py | Repository thật với cursor giả |
| Thời gian/mật khẩu validation, cache adapter không gọi SQL | test_task5_api_validation.py | Unit/HTTP không DB |
| Người chơi bị chặn báo cáo, giáo viên xem hạng, lọc leaderboard | test_task5_acceptance.py | HTTP qua TestClient với dữ liệu giả |
| Ôn tập dài, cuộn bằng phím, summary, empty/back, phục hồi clip | test_task5_review_ui.py | Pygame surface giả lập |
| Build allowlist, bảo vệ thư mục source, patch lặp an toàn | test_task5_build.py | Thư mục tạm |
| Server scoring import không kéo Pygame | test_task5_local.py | Subprocess |

## Chưa nghiệm thu end-to-end / không đủ điều kiện phát hành

1. Browser runtime: chưa có browser E2E runner; urllib còn đồng bộ, chưa chứng minh login/quiz/save trong WebAssembly hoạt động.
2. MySQL transaction/concurrency và migration: chưa chạy trên DB thử riêng. Cursor giả không chứng minh khóa InnoDB hay SQL migration chạy được.
3. Docker runtime: không phát hiện lệnh Docker trong môi trường; chưa build/run image.
4. Deduction: chưa chuyển toàn bộ đáp án qua API; không xác nhận điểm authoritative toàn game.
5. Quest: mới xác minh đủ đáp án đúng; chưa chứng thực đủ manh mối và thứ tự mở khóa bằng hành động server.
6. Đồng bộ JSON/DB desktop: chưa có transaction phân tán; lỗi mạng sau ghi dấu thưởng vẫn có thể làm mất thưởng.
7. Font Arial: chưa có bằng chứng quyền phân phối cho bản public.
8. Thống kê answer_log chỉ phản ánh một bản ghi/cặp user-question, không phải lịch sử mọi lần thử.

## Lỗi tìm thấy và sửa ngay trong nghiệm thu

- Build script in UTF-8 bị UnicodeEncodeError khi console Windows cp1252: cấu hình stdout/stderr UTF-8.
- Staging đổi tên main game thành game_desktop.py nhưng entry point vẫn import main: đổi sang chọn module game_desktop trong staging, main trên desktop; đặt API cùng origin và font shim trước import game trên web.

Không chạy ghi thử DB nhóm, không public ứng dụng, không tuyên bố tất cả Task 5 đã đạt. Build mới không tự cập nhật `.web-staging` cũ; muốn thử build mới phải cấu hình WEB_BUILD_DIR trỏ tới đường dẫn mới ở trên rồi restart Uvicorn.