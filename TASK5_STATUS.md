# Bổ sung refresh transaction trên nền 3f8cd0f

Edge canvas: progress/save trước backend và mười ca refresh trong transaction
commit/rollback của progress/quiz/clue/quest/review đều PASS, không pageerror.
Barrier chỉ có ở entry point test riêng, không endpoint production, bị loại khỏi
WASM. 110 pytest + 7 subtest PASS; compile/build PASS. HUD đầy đủ chưa nghiệm thu.
Run 44995369143 đang In progress lúc kiểm tra; không có chứng nhận CI cho code mới.
FINAL P1 ACCEPTED NO; READY FOR CONTROLLED STAGING NO; chưa deploy.

# Cập nhật nền 5ceb43b

Run 44992851127 SUCCESS được xác minh qua trang GitHub công khai; không dùng để
chứng nhận code mới. Thêm chờ scene/session sẵn sàng trong harness để tránh race
Notebook/map. Edge regression gồm bốn timeline PASS trên build sạch.
Refresh trước backend quiz/clue/quest/review PASS canvas; trong transaction chưa thử.
Tải 8 tài khoản 112/112; 16 tài khoản hai đợt tối đa 8 người: 224/224, không lỗi.
109 pytest + 7 subtest PASS. HUD đầy đủ và CI commit mới chưa nghiệm thu.
FINAL P1 ACCEPTED: NO; READY FOR CONTROLLED STAGING: NO. Không deploy.

# Cập nhật Final P1 trên nền 6ee4351

- Bốn ca canvas A/B pending quiz/clue/quest/review: PASS Edge, backend commit thật.
- Bốn ca canvas refresh sau commit tương ứng: PASS Edge, login khôi phục đúng dữ liệu.
- 109 pytest + 7 subtest PASS; compile PASS. Không sửa gameplay/schema/công thức.
- CI đã thêm tám lượt, chưa chạy Linux cho code mới; chưa xác minh run 44991691041.
- HUD ngoài ba ô Map/confirmed cũ, refresh trước/trong commit và load 8/16 chưa thử.
- Chưa FINAL P1 ACCEPTED hoặc READY FOR CONTROLLED STAGING. Không deploy.

# Nghiệm thu UI bổ sung trên nền 472673b

Đã chạy Edge canvas A/B pending progress/save và refresh sau commit progress/save:
PASS với API/SQLite thật, không HTTP mock. Cả bốn timeline regression PASS.
Map/confirmed đã chụp và xem đủ 3 viewport, không che UI. Các ô HUD khác chưa thử.
109 pytest + 7 subtest PASS; compile/build PASS. CI cho thay đổi mới chưa chạy;
run 44989309207 chưa được xác minh do thiếu kết nối GitHub ACTIVE.
Chưa tuyên bố toàn bộ Final P1 hoặc READY FOR CONTROLLED STAGING.

# Kết quả bổ sung hardening hiện tại

- Nền Git: `63990ad`, nhánh `improve/task5-release-readiness`; working tree sạch khi bắt đầu.
- Guard generation được kiểm tra ngay sau response GET/POST, không chỉ trước khóa ghi.
- Callback task cũ không đẩy lỗi vào tài khoản mới; logout xóa hàng đợi lỗi cũ.
- Pytest: 109 PASS, 0 FAIL, 0 SKIP, 7 subtest PASS; compile và build sạch đạt.
- Edge + FastAPI/SQLite thật: harness UI hiện có đạt, gồm bốn timeline, không pageerror.
- Network harness hiện có đạt; không dùng fetch để khẳng định đã test canvas account switch.
- Tải HTTP thật: 4 tài khoản, 52/52 request thành công; retry review/quiz đồng thời,
  quest lặp không thưởng thêm; integrity/foreign keys đạt.
- CI bổ sung bước tải SQLite; chưa chạy GitHub Actions cho các thay đổi của lượt này.
- Còn thiếu canvas A/B pending, refresh giữa từng write, HUD mọi scene/trạng thái/viewport.
  HTTPS staging chưa triển khai. Không tuyên bố hoàn tất toàn bộ final P1.

# Kết quả sửa và giới hạn nghiệm thu Task 5

## P1 final bổ sung mới nhất
101 test + 7 subtest local PASS. Edge canvas cả bốn timeline có session_id/confirmed
quest PASS. Network harness commit-thật/mất-response, offline, abort, 400/401/503,
timeout và relogin restore PASS (phạm vi fetch, không phải toàn bộ HUD UI fault matrix).
Cleanup bounded retention 7 ngày, expiry renewal/TTL monotonic, stale queued write guard.
Không đổi ScoringEngine/history/IDs; sửa current_loc_id và pin chồng được chứng minh bởi UI.
Xem đầu TASK5_ACCEPTANCE.md cho ma trận chưa thử; không coi toàn bộ P1 đã hoàn thành.

## P1 mới: phiên giờ server và trạng thái lưu
Migration 007 + /quiz/start, session bound user/question, 1h expiry, giới hạn 12 mở,
atomic score/session, replay không thưởng lại. Client timing không còn quyết định tốc độ
tại HTTP; legacy vẫn chấm nhưng không thưởng tốc độ. ScoringEngine giữ nguyên.
HUD trạng thái lưu và reconciling; transport ghi lỗi đọc lại progress, không tự thưởng.
96 test + 7 subtest PASS. Xem đầu TASK5_ACCEPTANCE.md cho run CI và các phạm vi chưa đạt.
Chưa hoàn tất toàn bộ browser fault matrix/timeline UI/session cleanup; không tự public.

## Release readiness — nhánh improve/task5-release-readiness
- Nền origin/main 142976c, working tree sạch trước sửa; không sửa main.
- P0: HTTP content/questions/catalog không trả answer/dap_an_dung/correct_index hoặc
  giải thích trước chấm. Build loại đáp án fallback/tuple timeline khỏi WASM; code server
  vẫn giữ đáp án chuẩn. Deduction và timeline online dùng kết quả API, không fallback chấm local.
- P0: collect_clue giữ state server _task5; password không strip, không giới hạn âm thầm 35 ký tự.
- P1: save queued/pending/confirmed/failed; chỉ cập nhật cache sau đọc server; timeout
  đọc lại progress, không repost thưởng; generation/revision chặn response phiên cũ.
- Local: 89 PASS + 7 subtest, compile/build đạt. Edge UI mật khẩu q/Q và khoảng trắng
  đầu/cuối đạt; API toàn tuyến 9 quest SQLite thật đạt.
- Run Linux 44915991970 tại 2886252 completed/success: pytest/compile/Pygbag/Chromium UI,
  Docker và persistence restart SUCCESS. Xem TASK5_ACCEPTANCE.md cho giới hạn nghiệm thu.
- Chưa làm: phiên thời gian server; client vẫn khai so_giay, thưởng tốc độ có thể gian lận.
  Chưa nghiệm thu browser network fault toàn bộ/review-timeout/refresh giữa ghi. P2 không mở rộng.

## Trạng thái mới nhất: Chromium Linux PASS
Run 44913145381 tại f4a255f SUCCESS toàn bộ: Python/SQLite, compile, Pygbag,
Chromium UI thật không mock, Docker build và SQLite volume sau restart.
Lỗi cũ là văn bản hoa/thường trong đường nhập SDL web/harness, không phải backend treo:
login gửi dữ liệu lowercase và nhận 401 đúng, vì vậy không phát sinh review request.
Đã dùng TEXTINPUT cho web và Shift+key hoa đúng trong harness. Assert credential match,
login/review 200 và pageerror rỗng được giữ nguyên. Local 82 test + 7 subtest PASS.
Xem đầu TASK5_ACCEPTANCE.md; các ghi chú Linux FAIL phía dưới là lịch sử.

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