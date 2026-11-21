# Kết quả sửa và giới hạn nghiệm thu Task 5

## Cập nhật mới nhất (ưu tiên hơn các ghi chú lịch sử bên dưới)

Chính sách quest/tiến độ đã siết ở server: chặn tự khai completed, chặn địa điểm khóa, kiểm ID manh mối chính thức/đủ manh mối trước complete, suy ra năm server, lọc khóa scoring nội bộ. 57 test + 7 subtest đạt, Edge mock-actions và desktop smoke đạt. Chưa chứng minh hành động đọc/thu thập thật hoặc MySQL concurrency; ID cache browser còn cần đồng bộ nội dung DB. Xem biên bản chi tiết.

Transport browser cho quiz/retry/save/quest/leaderboard/refresh review đã được nối fetch async qua task/poll hoặc task nền. 43 test + 7 subtest đạt; Edge thật login→review→retry→leaderboard với HTTP giả đạt, không pageerror. Save queued vẫn cần theo dõi kết quả/lỗi; quiz/save chưa E2E với DB thật. Các mục server authoritative deduction/manh mối/thứ tự mở khóa và MySQL integration vẫn còn. Xem TASK5_ACCEPTANCE.md.

## Đã sửa bằng mã và test hồi quy

- Lazy import UI: server không cần Pygame chỉ để import scoring/repository.
- Kho local có dấu thưởng bền vững; JSON ghi file tạm và thay thế nguyên tử.
- API profile không ghi JSON local; đăng xuất xóa cache adapter.
- Phòng ôn tập xuống dòng, cuộn danh sách/chi tiết, tổng kết TAB, rect dùng chung để vẽ và bấm.
- Không tự sinh câu sai mẫu vào hồ sơ thật.
- Đồng bộ điểm ôn tập local về Game và gọi lưu khi đổi điểm.
- Chặn thời gian 0, âm, NaN/Infinity; giới hạn bcrypt theo byte UTF-8.
- Lưu chuỗi đúng server trong khóa nội bộ `_task5`; client không được ghi đè khóa này.
- Quiz Task 4 dùng đồng hồ thực thay vì gán 1 giây; retry/quiz khóa progress trước để giảm deadlock.
- Quest kiểm tra địa điểm và đủ đáp án đúng của bộ câu server trước khi thưởng; không tin tên/năm client.
- Trang giáo viên có `/teacher/login`, token chỉ giữ trong RAM của trang; báo cáo vẫn được phân quyền.
- Build staging theo allowlist và `.dockerignore` loại secret, profile, dump khỏi container.

## CHƯA nghiệm thu, không public như bản hoàn chỉnh

**Cập nhật:** Browser first-frame đã chạy thật bằng Playwright/Edge: ready=true, không pageerror. Xem `TASK5_ACCEPTANCE.md`. Kiểm tra này không xác nhận các thao tác mạng/DB.

- Transport browser vẫn dùng urllib đồng bộ: cần chuyển toàn bộ call-site sang async browser fetch, không chỉ thêm một hàm async rồi bỏ mặc caller.
- Đã thêm `task5/browser_client.py` async có timeout và kiểm thử giải mã; adapter hiện tại chưa chuyển sang dùng lớp này, không công bố là transport đã hoàn tất.
- Cập nhật: adapter và LoginScene đã nối fetch cho auth browser, cache review/progress phục vụ áp dụng phiên; Edge UI login với HTTP giả đã vào bản đồ thành công. Quiz/retry/save/leaderboard chưa chuyển xong, không coi toàn bộ transport hoàn tất.
- Luồng deduction chưa nộp toàn bộ câu hỏi qua API; không thể công bố tất cả điểm game đã authoritative.
- Quest mới xác minh quiz, chưa chứng thực thu nhặt manh mối/thứ tự mở khóa bằng hành động server-side.
- Tiến độ client gửi vẫn là dữ liệu tham khảo; cần chính sách xác minh địa điểm/manh mối đầy đủ trước production.
- Chưa chạy integration test transaction/concurrency trên MySQL riêng và browser E2E; unit/mock không thay thế được.
- Font Arial lấy từ Windows: cần kiểm tra quyền phân phối hoặc thay bằng font mở có license kèm theo trước public.
- Hai tài nguyên điểm (JSON dấu thưởng và DB điểm desktop) chưa có transaction chung; mất mạng sau khi claim có thể làm mất thưởng thay vì nhân đôi.
- answer_log có một hàng/cặp user-question nên thống kê chỉ phản ánh trạng thái hiện tại, không phải mọi lần sai.

## Chạy kiểm tra

`python -m pytest -q tests`

`python -m compileall -q task5 tests main.py main_web.py scenes/review_scene.py`

Chuẩn bị gói sạch: `python -m task5.build_web --stage-only`.
Build: `python -m task5.build_web` (chỉ xác nhận đóng gói, chưa phải chứng nhận chạy web).
Không sử dụng DB dùng chung để thử. Database integration cần `game_dev` được tạo riêng, không tự fallback sang DB nhóm.