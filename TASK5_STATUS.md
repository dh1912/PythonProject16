# Kết quả sửa và giới hạn nghiệm thu Task 5

## Kết quả cuối lượt Q / clean-worktree / Linux
- Code HEAD ea8d86f: worktree riêng pytest 81 PASS + 7 subtest, compile/build/Edge UI
  q/Q PASS; không dựa vào file chưa commit hoặc database cá nhân.
- Run Linux 44911172510: pytest/compile/Pygbag/Docker build/container persistence sau restart
  đều SUCCESS. Chromium UI FAIL timeout chờ /review/me sau thao tác đăng nhập.
- Đã thử explicit mouse focus trên Linux, lỗi vẫn còn; không coi workflow tổng thể PASS.
  Chẩn đoán công khai có traceback, nhưng chưa đủ để khẳng định nguyên nhân SDL/input.
- Commit mới: faeb1e2 (sửa Q), 4f0d05c (CI diagnostics), ea8d86f (Linux focus harness).
  Tất cả đã push nhánh thường. Không merge main/deploy public.

## HEAD độc lập và lỗi Q
- Nhóm v6/manifest/gameplay được thành viên chốt trong 2167792; đầu lượt Git sạch.
- faeb1e2 sửa Q ở hai tầng Game/LoginScene; 4 regression test mới. Worktree riêng + venv
  mới: 81 PASS, 7 subtest PASS, compile/build PASS, Edge q/Q Tab/Backspace/Enter PASS.
- Tất cả 9 quest API qua Edge/SQLite thật cũng đạt trên worktree HEAD này.
- Nhánh đã push, run 44910700587 thực sự chạy Linux; pytest/compile/Pygbag success.
  Browser Linux và Docker/persistence chưa kết luận trong lúc chờ workflow.

## Bổ sung CI/UI và manifest trong lượt hiện tại
- Phân loại Git: nhóm v6/gameplay và ảnh nghiệm thu tồn tại trước lượt này được giữ nguyên;
  commit CI/UI chỉ chứa workflow, helper container/UI, sửa chọn sự kiện đại diện và tài liệu.
- 77 test PASS, 0 FAIL, 0 SKIP; 7 subtest PASS. Compile và Pygbag build PASS.
- Edge UI thật + API/SQLite tạm: login, Notebook chỉ đọc, điều tra, quiz sai/đúng,
  quest server xác nhận, review, leaderboard, vào màn điều tra thứ hai PASS; page_errors=[].
- Sửa lọc active cho DAL/catalog/Notebook; test phát hiện JOIN thiếu ma_su_kien và đã sửa.
  Những file dùng chung có diff v6 từ trước được giữ chưa commit để không gộp nhầm.
- CI Linux đã chuẩn bị pytest/compile/Pygbag/Chromium UI/Docker/persistent-volume restart.
  Docker local và GitHub Actions thực thi: CHƯA KIỂM THỬ. Không push/merge/public.

## Trạng thái hiện hành: nhánh fix/sqlite-web-deploy

### Trạng thái mới nhất (2026-11-21)
- Historical content migration 006 đã bổ sung đúng dữ liệu được thay thế trong migration
  Task 4 004, theo cách additive và manifest; không xóa dữ liệu người chơi hoặc bản ghi cũ.
- SQLite sạch: 9 địa điểm/30 sự kiện; 16 clue và 12 câu hỏi Task 4 mới được đưa vào active
  content, ID ổn định theo manifest; tất cả 9 địa điểm có câu hỏi và clue chính thức hiện hành.
- Edge + FastAPI + SQLite file tạm chạy toàn tuyến quest qua API: 9/9 hoàn thành, điểm/tiến độ
  tải lại, quest/review thưởng không lặp, leaderboard; không JS page errors.
- `pytest`: 76 PASS, 0 FAIL, 7 subtest PASS; compile/build đạt.
- Đây là E2E fetch từ browser thật, không phải click UI thủ công cho 9 địa điểm. Docker chưa
  chạy do thiếu Docker CLI; public deployment chưa thực hiện.

Backend/DAL đã chuyển SQLite, không yêu cầu MySQL. Các đoạn MariaDB phía dưới là lịch sử.
70 test chính PASS, 7 subtest PASS, 0 FAIL, 0 SKIP. Build sạch và Edge với API/SQLite
thật trên file tạm đạt; xem TASK5_ACCEPTANCE.md và DEPLOY_WEB.md.

Giữ công thức ScoringEngine, JWT/bcrypt, phân quyền, review và task/poll web từ main.
Giữ thuật toán Task 3 và Quest/Timeline Task 4; Notebook thêm data_provider, phím N,
không mở SQLite trong browser, chỉ xem tư liệu không cộng tiến độ.

DB mới tự tạo/seed, DB cũ backup trước migration 5, UPSERT bảo toàn task state,
legacy plaintext yêu cầu đặt lại mật khẩu. Seed nội dung trích game.sql commit c7813c3,
không seed tài khoản hoặc sửa nội dung lịch sử tùy ý.

Chưa kiểm Docker runtime vì không có Docker CLI; chưa deploy public. Không kết luận
production-ready toàn bộ 11 địa điểm; UI E2E thật mới xác nhận quest đầu.

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