# Final P1: bổ sung canvas trên nền 6ee4351

Working tree sạch khi bắt đầu; local và origin cùng `6ee4351`.
Không sửa gameplay, ScoringEngine, schema hoặc dữ liệu lịch sử trong lượt này.

| Endpoint | Canvas A logout/B login, giữ response sau commit | Canvas refresh sau commit |
|---|---|---|
| /quiz/submit | PASS Edge | PASS Edge |
| /clues/collect | PASS Edge | PASS Edge |
| /quest/complete | PASS Edge | PASS Edge |
| /review/retry | PASS Edge | PASS Edge |
| /progress/save | Giữ kết quả lượt trước | Giữ kết quả lượt trước |

Tám lượt mới dùng FastAPI/SQLite tạm, request UI thật qua canvas; `route.fetch()`
đã hoàn tất backend trước khi giữ response. Không mock nghiệp vụ. A quay map bằng
ESC rồi L logout, B nhập qua bàn phím/click. B score/completed/clue/review vẫn trống;
API A giữ đúng snapshot sau commit; không pageerror. Refresh login lại bằng canvas
khôi phục đúng snapshot tiến độ/review, không tự nộp lại thưởng.

Lỗi harness mới: connection kiểm tra integrity không đóng khi dùng `with conn`.
Đã dùng closing và chạy lại cả bốn ca A/B mã thoát 0. Không phải lỗi transaction game.

Ma trận HUD (mỗi ô áp dụng cho cả 1280×900 / 1366×768 / 1920×1080):

| Scene | queued | pending | confirmed | failed | reconciling |
|---|---|---|---|---|---|
| Map | NOT TESTED | NOT TESTED | PASS lượt trước | NOT TESTED | NOT TESTED |
| Investigation | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Deduction | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Timeline | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Review | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

Refresh trước/trong commit của bốn endpoint: NOT TESTED canvas. Không suy ra từ ca
sau commit. Load 8/16 tài khoản: NOT TESTED; không bypass quota 5 login/phút cùng IP.
Pytest cuối: 109 PASS / 0 FAIL / 0 SKIP, 7 subtest PASS; compile PASS.
Harness chạy trên build hiện có đã nghiệm thu của nền, không sửa nguồn game đóng gói.
Workflow bổ sung tám lượt trên Linux, nhưng chưa chạy cho code mới. Run 44991691041
chưa xác minh vì công cụ GitHub chưa có kết nối ACTIVE. Không ghi CI/Docker PASS.
Kết luận: chưa FINAL P1 ACCEPTED, chưa READY FOR CONTROLLED STAGING do HUD và
refresh trước/trong commit, CI Linux mới còn thiếu bằng chứng.

# Bổ sung nghiệm thu canvas trên nền 472673b

- Đầu lượt HEAD local/remote cùng `472673b`, working tree sạch. Commit này chỉ
  bổ sung artifact, không thay code so với `dd0bbb6`.
- Edge thật, FastAPI/SQLite tạm: UI A gửi `/progress/save`, backend commit thật qua
  `route.fetch()`, giữ response; A quay map bằng ESC, logout L, B đăng nhập bằng
  click/phím. Thả response A: B vẫn score=0, completed=0, HUD confirmed; đọc API
  độc lập xác nhận A giữ dữ liệu đã commit, B không nhận dữ liệu A. PASS.
- UI refresh sau commit `/progress/save` nhưng trước response: reload rồi login B
  bằng canvas, đọc lại tiến độ bằng API và đối chiếu điểm UI. PASS.
- Map/confirmed: chụp và xem ảnh 1280×900, 1366×768, 1920×1080. Nhãn tiếng Việt
  đọc được, không che nội dung/nút. PASS cho đúng ba ô này, không suy rộng ma trận.
- UI regression hiện có: đăng nhập, Notebook, quest đầu, review, Bảng Vàng và bốn
  timeline đều PASS; `page_errors=[]`. Build sạch và compile PASS.
- Pytest cuối: 109 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS. Còn cảnh báo TestClient.
- Chưa thử canvas A/B cho quiz/clue/quest/review; refresh trước/trong commit từng
  write; HUD các scene/trạng thái còn lại. Không gọi các ca service/fetch là UI E2E.
- Run 44989309207 chưa được xác minh bằng công cụ GitHub trong lượt này vì kết nối
  chưa ACTIVE; CI/Docker cho thay đổi mới CHƯA CHẠY, không dùng SUCCESS lịch sử.
- Chưa READY FOR CONTROLLED STAGING theo tiêu chí Final P1 đầy đủ của yêu cầu.

# Nghiệm thu bổ sung: response muộn và tải SQLite

Nền `63990ad`, nhánh `improve/task5-release-readiness`. Đây là kết quả mới, không
thay thế giới hạn được ghi ở các lần nghiệm thu trước.

| Kiểm tra đã chạy | Kết quả |
|---|---|
| Pytest | 109 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS |
| Compile / build Pygbag sạch | PASS |
| Edge UI + FastAPI/SQLite tạm, gồm bốn timeline | PASS, không pageerror |
| Network harness hiện có | PASS, 14 dòng kết quả, bao gồm hai clue |
| Tải HTTP thật | 4 tài khoản, 52/52 request, 0 HTTP 503 |
| Thời gian tải local | median 78.605 ms, p95 313.56 ms, max 360.58 ms |
| SQLite integrity/foreign keys sau tải | PASS |
| A/B response muộn cho 5 POST và GET tiến độ/review | PASS mức coroutine/service |
| Canvas A/B logout pending | CHƯA NGHIỆM THU |
| Refresh đang ghi từng quiz/review/quest | CHƯA NGHIỆM THU UI |
| HUD 5 scene × 5 trạng thái × 3 viewport | CHƯA NGHIỆM THU |
| Docker/Linux CI của commit mới | CHƯA CHẠY |
| Staging HTTPS | CHƯA TRIỂN KHAI |

Đã sửa guard sau transport và cách ly lỗi callback task cũ. Harness tải ban đầu
thành công nghiệp vụ nhưng lỗi cleanup Windows do context manager SQLite không
đóng connection. Đã dùng `contextlib.closing`, chạy lại hoàn tất mã thoát 0.
Không thay đổi ScoringEngine, schema, nội dung lịch sử hoặc dữ liệu người chơi.
Artifact `data/sqlite-load-result.json` chỉ chứa endpoint/status/timing, không token,
tên tài khoản, mật khẩu hoặc nội dung trả lời. Không commit ảnh/log tài khoản thử.

# Biên bản nghiệm thu Task 5 trên workspace hiện tại

## Final P1 bổ sung (nền 2679b3f)
- Local: 101 pytest PASS, 0 FAIL, 0 SKIP; 7 subtest PASS. Compile/build và Edge UI đạt.
- Cleanup lazy tối đa 100/lần, expiry hơn 7 ngày; không xóa phiên live/replay còn retention,
  không xóa answer_log. Test lặp 100/5/0, integrity/foreign_keys sạch. TTL dùng monotonic
  client theo remaining_seconds server; hết hạn thông báo mở mới, không auto nộp.
- Lỗi thật đã sửa: vào địa điểm chưa lưu current_loc_id nên collect trả 400; lưu địa điểm
  trước clue. Pin/label chồng làm Dinh Độc Lập vào Bến Nhà Rồng; ưu tiên pin gần nhất.
- Edge UI canvas: kéo bốn thẻ, Enter, ba câu/session_id và confirmed quest tại cả Pác Bó,
  Ba Đình, Điện Biên Phủ, Dinh Độc Lập. Fixture DB mở khóa các quest trước để cô lập test;
  không dùng fixture chứng minh đã chơi toàn hành trình. Không gọi Game để nhảy scene.
- Browser network-matrix với FastAPI/SQLite thật (không fulfill kết quả nghiệp vụ giả):

| Case | Thao tác/phạm vi | Kết quả local |
|---|---|---|
| A offline | save | PASS |
| B abort trước server | save, tiến độ không đổi | PASS |
| C commit rồi abort response | start/quiz/review/clue/save/quest, replay không thưởng lặp | PASS |
| D 400 | quiz token không hợp lệ | PASS |
| E 401 | save không token | PASS |
| F 503 | save với writer SQLite thật giữ khóa | PASS |
| G timeout sau commit | save, đọc lại progress | PASS |
| H double click | UI cũ + concurrency SQLite; chưa mọi endpoint trên browser | MỘT PHẦN |
| I logout pending/account switch | unit queued-generation; chưa canvas browser | CHƯA ĐỦ |
| J refresh pending | refresh sau ghi/lost response restore; chưa refresh đang xử lý mọi write | MỘT PHẦN |

- Matrix dùng fetch trong browser, không chứng minh HUD/game scene fault response đồng thời.
  HUD states được test service coroutine, có ảnh confirmed; resize/failure HUD mọi scene chưa đủ.
- CI c701bfd run 44924084646: Chromium bốn timeline và network step SUCCESS;
  run a0c6624 mới nhất 44924401030 cần kết quả cuối trước khi ghi Docker PASS.
- Kết quả cuối a0c6624: https://github.com/dh1912/PythonProject16/actions/runs/44924401030
  completed/success; pytest/compile/Pygbag, Chromium bốn timeline, browser network matrix,
  Docker build, container health và persistence restart đều SUCCESS. Artifact lỗi SKIPPED
  do không có lỗi, không có assertion/test bị tắt. Commit tài liệu sau đó không đổi code.
- Rủi ro còn: chưa đầy đủ A–J cho auth/register/leaderboard, logout/refresh canvas giữa write;
  expiry desktop online chưa có UX tự gia hạn như browser; thời gian không chứng minh người đọc.
  Chỉ phù hợp staging nội bộ có kiểm soát sau review, không tuyên bố P1 hoàn tất tuyệt đối.

## P1 phiên câu hỏi và HUD — cập nhật mới nhất
- Nền 9aa003c, đầu lượt Git sạch. Không sửa ScoringEngine/ID lịch sử/quest.
- Migration 007 tạo question_sessions, backup trước upgrade; BEGIN IMMEDIATE khóa chấm,
  lưu response + điểm + used choice trong một transaction. Token ngẫu nhiên 32 byte,
  chủ sở hữu/câu hỏi/expiry 1 giờ, tối đa 12 phiên mở; start lặp dùng lại đồng hồ cũ.
- POST /quiz/start không trả đáp án. POST /quiz/submit có session_id dùng thời gian server,
  bỏ qua so_giay giả; legacy không session chỉ có điểm cơ bản/chuỗi, không thưởng tốc độ.
  Replay cùng lựa chọn không thưởng thêm và trả tổng điểm hiện tại; khác lựa chọn bị từ chối.
- Game chuẩn bị session khi câu xuất hiện, không phải khi bấm nộp. Browser/desktop online
  có điểm nối; lỗi start có thể dùng legacy an toàn không tốc độ. Review vẫn +15 một lần.
- HUD có queued/pending/confirmed/failed/reconciling tiếng Việt. Quiz/clue/review/quest lỗi
  transport đọc progress, không blind retry. Response khác generation không áp dụng cache.
- 96 pytest PASS, 0 FAIL, 0 SKIP; 7 subtest PASS; compile đạt.
  SQLite thật test expiry/owner/question/token giả, hai submit đồng thời, server timestamp,
  restart bằng process mới, mất response sau commit/replay, rollback trigger, backup v7.
- Build/Edge thật đạt tại 497c0c0; run Linux 44919986180 SUCCESS tất cả Python/Pygbag/
  Chromium/Docker/persistence. Run mới a351f5e siết assert quiz UI đầu có session_id:
  https://github.com/dh1912/PythonProject16/actions/runs/44920390975 .
- Kết quả cuối a351f5e: completed/success. Chromium có start/session_id thật, không mock;
  pytest/compile/Pygbag/Docker/container persistence đều SUCCESS. Artifact lỗi SKIPPED
  vì không có lỗi, không phải vô hiệu hóa test.
- Chưa nghiệm thu đầy đủ: UI timeline timed session; tất cả browser fault 400/401/503,
  refresh/logout giữa từng write; expiry chưa có auto-renew UI; session cũ chưa có cleanup.
  Thời gian đo từ start request không chứng minh người chơi đọc câu; người chơi biết trước
  câu có thể start muộn. Đồng hồ UTC server cần ổn định. Không tuyên bố chống gian lận tuyệt đối.
  P1 chưa đủ để kết luận staging không giới hạn; chỉ chuẩn bị staging có kiểm soát sau review.

## Release readiness P0/P1 — 2886252
- Nền origin/main 142976c, nhánh mới improve/task5-release-readiness. Không merge/deploy.
- Lỗi xác minh: public API có đáp án; clue state bỏ _task5; form strip password;
  cache progress cập nhật trước xác nhận. Đã sửa, giữ ScoringEngine/schema/ID lịch sử.
- Test mới: public recursive no-answer, server streak qua collect rồi câu tiếp +36,
  bcrypt chính xác tiếng Việt/khoảng trắng/hoa-thường, HTTP forged score bị bỏ qua,
  client _task5 bị từ chối, relogin giữ state, WAL backup integrity/restore,
  build không có đáp án embedded, timeout-after-commit đọc lại không repost.
- 89 pytest PASS, 0 FAIL, 0 SKIP; 7 subtest PASS; compile/build đạt.
- Một lượt local Edge abort login sau timeout transport 5 giây trong lúc máy chậm;
  lượt chạy lại đạt không thay timeout/assertion. Không coi đây là đảm bảo mạng luôn sẵn sàng.
- Edge UI SQLite thật: password q/Q + khoảng trắng đầu/cuối khớp tuyệt đối,
  login/review/quest/leaderboard đạt, page_errors=[]; toàn tuyến 9 API quest đạt.
- Linux run: https://github.com/dh1912/PythonProject16/actions/runs/44915991970
- Kết quả cuối run tại 2886252: completed/success. Pytest, compile, Pygbag, Chromium UI,
  Docker build, container health/lưu/đăng nhập lại sau restart volume đều SUCCESS.
  Artifact chẩn đoán SKIPPED vì không có lỗi; không có test bị skip để làm xanh.
- Giới hạn: chưa triển khai question-session timestamp server; chưa chống giả tốc độ.
  Queued/pending hiện là trạng thái service, chưa có chỉ báo UI chuyên biệt đầy đủ.
  Lỗi timeout save đọc lại nhưng vẫn đánh dấu failed vì chưa chứng minh payload đã lưu đủ.
  Chưa test browser thật tất cả lỗi 400/401/503, logout/refresh giữa từng loại write;
  test async không thay thế các kịch bản mạng thật này. Không tuyên bố toàn bộ P1 hoàn thành.

## Chromium Linux đã sửa và nghiệm thu — f4a255f
- Run thành công: https://github.com/dh1912/PythonProject16/actions/runs/44913145381 .
  Pytest, compile, Pygbag, Chromium UI SQLite thật, Docker build và container persistence
  qua restart đều SUCCESS. Step artifact lỗi SKIPPED vì không có lỗi, không phải skip test.
- Nguyên nhân xác minh bằng run chẩn đoán 44912530045: POST /auth/login có gửi và trả 401;
  không có /review/me. Canvas có focus đúng, username dài 16/password dài 30, không rơi
  ký tự. Payload khớp bản lowercase của fixture nhưng không khớp đúng hoa/thường.
  Loading được giải phóng sau khi nhận 401, không phải backend treo.
- SDL web không nên dùng KEYDOWN.unicode như văn bản đã nhập. Form web chuyển sang
  TEXTINPUT (Shift/Caps Lock/IME), KEYDOWN chỉ xử lý phím điều khiển; desktop giữ nguyên.
  Harness dùng phím hoa thực với Shift và key='Q', không key='q' khi mong nhập 'Q'.
  Thử chỉ Shift+key thường không sửa được lỗi; đã tái hiện 401 trên Edge.
- Không nới lỏng xác thực password, không bỏ assertion: login phải HTTP 200, payload
  username/password phải khớp chính xác, /review/me phải 200 và game phải sang map.
- Chẩn đoán allowlist: endpoint/method/status/thời gian, requestfailed, pageerror,
  console error, kích thước canvas/focus, độ dài ô và loading; không headers/token/body.
  Timeout chụp ảnh và giữ FastAPI stdout/stderr. Chế độ UI-state chỉ bật ?acceptance=1,
  không có nội dung username/password hoặc token.
- Local: 82 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS, compile/build và Edge UI mã thoát 0.
  Regression mới kiểm TEXTINPUT giữ q/Q/Đ và không ghi đôi từ KEYDOWN.
- Commit chẩn đoán: 5c40f5f, c84bc62, ca16d81; b214e07 thử Shift; f4a255f sửa cuối.
  Các phần schema/ScoringEngine/quest/nội dung lịch sử không thay đổi trong lượt này.

## Kết quả Linux cuối lượt — cập nhật thay thế trạng thái đang chờ
Run https://github.com/dh1912/PythonProject16/actions/runs/44911172510 tại ea8d86f:
- SUCCESS: dependency install, pytest, compile, Pygbag, Docker build.
- SUCCESS: container SQLite health, đăng ký/chấm quiz/lưu clue/quest, restart volume,
  đăng nhập lại và so sánh toàn bộ tiến độ bằng ci_container_check.
- FAIL: Chromium UI timeout chờ /review/me sau thao tác auth. Đổi Tab/Enter thành
  explicit canvas mouse focus trên Linux chưa giải quyết được. Không bỏ assertion,
  không đổi thành HTTP mock, không ghi workflow tổng thể PASS.
- Worktree riêng ea8d86f: 81 pytest + 7 subtest PASS, compile/build và Edge UI q/Q PASS.
  Tất cả thử trên DB tạm; local Windows không có Docker nhưng Docker Linux đã chạy thật.
- Warning còn lại: Starlette/httpx và Node 20 của các action version hiện tại.
- Giới hạn phát hành: Chromium Linux UI chưa đạt; cần đọc thêm browser/SDL diagnostic.
  Không kết luận production-ready và chưa deploy.

## Nghiệm thu từ Git HEAD độc lập: faeb1e2
- Đầu lượt working tree sạch: thành viên đã commit toàn bộ nhóm v6/manifest/gameplay/test
  trong `2167792`, không còn nhóm thay đổi cũ cần tự gộp. Giữ nguyên commit này.
- `faeb1e2`: Game không bắt Q ở scene login; LoginScene chỉ cho Q thoát khi không ô nào
  có focus. Ô username/password/đăng ký nhận q/Q bình thường; giữ Tab/Backspace/Enter.
- Worktree detached tại faeb1e2: `C:/Users/Admin/PycharmProjects/PythonProject/task5-clean-acceptance`.
  Tạo venv mới và cài requirements server/client, pygbag, playwright, pytest-subtests.
- Từ worktree: 81 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS; compile/build Pygbag mã thoát 0.
  Test SQLite dùng DB mới/tạm: active manifest, dữ liệu legacy, tiến độ, concurrency,
  thưởng một lần và khôi phục process mới đều thuộc suite này.
- Edge UI thật: username và password chứa cả q/Q, Tab chuyển focus, Backspace xóa,
  Enter đăng nhập thành công; Notebook/điều tra/quiz/review/quest/Bảng Vàng đạt,
  `page_errors=[]`, mã thoát 0. Không HTTP mock.
- Edge fetch + FastAPI/SQLite tạm: 9/9 địa điểm đạt, restore và reward-once đạt, exit 0.
- Push nhánh thường faeb1e2 thành công. Run Linux thật:
  https://github.com/dh1912/PythonProject16/actions/runs/44910700587
  Đã xác nhận pytest/compile/Pygbag success; Chromium/Docker đang chờ kết quả khi ghi mục này.
- Worktree kiểm thử chỉ sinh thay đổi JSON kết quả UI; không dựa vào DB hoặc mã chưa commit.
  Không merge main, không force push, không public.

## Nghiệm thu bổ sung UI/CI/manifest
- Pytest toàn bộ: 77 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS; 1 warning Starlette/httpx.
- Compile và build Pygbag sau sửa: mã thoát 0.
- `python -m task5.check_sqlite_ui`: Edge headless, API SQLite tạm thật, không mock,
  mã thoát 0. Thao tác bằng canvas/keyboard: login -> N Notebook -> điều tra -> quiz sai
  rồi đúng -> chờ quest hoàn thành -> ENTER về map -> R review đúng -> B leaderboard
  -> vào điều tra thứ hai. Notebook không thay đổi điểm/tiến độ; page_errors=[].
- Harness gặp lỗi điều hướng ESC sai màn và password ngẫu nhiên chứa phím q (game dùng
  Q để thoát); fixture dùng mật khẩu không chứa q, dùng ENTER đúng hướng dẫn game.
  Giới hạn game hiện tại: phím Q toàn cục có thể gây thoát lúc nhập mật khẩu chứa q.
- Phát hiện ảnh địa điểm Hương Cảng ghi sự kiện 1862 dù clue năm 1930: sửa mapping ưu
  tiên sự kiện có clue chính thức, không thay đổi hàng lịch sử hoặc luật tính điểm.
- Manifest: test mới kiểm tra DAL, catalog, Notebook và bộ câu hỏi API chỉ trả ID active,
  đồng thời số hàng legacy trong SQLite không giảm. JOIN Notebook bổ sung ma_su_kien.
- CI workflow có quyền read-only, timeout, health polling thất bại rõ ràng và cleanup.
  Docker CLI không có; workflow chưa push/chạy trên GitHub nên KHÔNG ghi Docker/CI PASS.
- Bằng chứng UI cục bộ: data/sqlite-ui-result.json, sqlite-ui-notebook.png,
  sqlite-ui-board.png, sqlite-ui-next.png. Không có JWT/mật khẩu trong JSON kết quả.

## SQLite web — kết quả hiện hành (thay thế ghi chú lịch sử bên dưới)

### Cập nhật kiểm thử lịch sử v6 và toàn bộ địa điểm — 2026-11-21
- Thêm migration 006 additive và seed lấy trực tiếp từ `data/migrations/004_task4_complete.sql`;
  bản ghi manh mối/câu hỏi bị migration 004 thay thế được giữ lịch sử trong SQLite và chỉ
  các ID trong `content_manifest` được phục vụ làm bộ nội dung active. Không xóa tiến độ.
- DB sạch sau v6: 9 địa điểm, 30 sự kiện, 26 manh mối đang lưu (16 bản chính thức 004
  cùng các bản ghi legacy được giữ), 20 câu hỏi đang lưu (12 chính thức 004 và legacy),
  30 mốc lịch sử, 30 nguồn và 21 nhân vật lịch sử; foreign_key_check sạch.
- Cập nhật harness Edge: không còn tra câu timeline trong endpoint DB không chứa timeline;
  ID và đáp án fixture lấy từ cấu hình Task 4 chính thức, server vẫn tự xác minh đáp án.
  Tuân theo thứ tự mở khóa QuestManager: 1,2,3,4,5,6,7,8,9.
- Edge headless + FastAPI thật + SQLite tạm: đăng ký, câu sai/review +15 một lần,
  câu quiz, lưu đủ clue ID chính thức, hoàn thành từng địa điểm +30 một lần, tải tiến độ,
  đăng nhập lại và leaderboard: **9/9 quest PASS**, `page_errors=[]`, mã thoát 0.
- Matrix: địa điểm 1–3,5,7 dùng bộ câu hỏi SQLite tương ứng; 4 Pác Bó, 6 Ba Đình,
  8 Điện Biên Phủ, 9 Dinh Độc Lập dùng ba ID `task4:` chính thức mỗi nơi. Manh mối DB
  được lưu theo ID: lần lượt 2,1,1,4,1,4,1,4,4.
- Test toàn cục sau cập nhật: **76 PASS, 0 FAIL, 7 subtest PASS**, 1 warning deprecation
  Starlette/httpx. Compile và Pygbag build mới PASS.
- Phạm vi: game runtime trong Edge được khởi tạo thật; chuỗi 9 quest được thực hiện bằng
  `fetch` trong tab browser với API/SQLite thật, không HTTP mock. Đây chưa phải thao tác UI
  thủ công từng câu cho cả 9 địa điểm. Docker vẫn chưa được chạy trên máy này.

### Git
- Workspace ban đầu sạch, feature/clue-notebook-system ở 71d7b66.
- Fetch origin; main mới nhất 5f65cec đã merge Notebook và cải tiến Task 5.
- Tạo fix/sqlite-web-deploy từ origin/main, không reset/force push/merge main.

### Lỗi và sửa
- authenticate_user bỏ qua password: xác minh bcrypt bắt buộc, hash thiếu/legacy rõ từ chối yêu cầu reset.
- INSERT OR REPLACE làm mất state: UPSERT + BEGIN IMMEDIATE, giữ _task5 và clue_ids.
- Repository MySQL xung đột SQLite: thay placeholders, khóa ghi, UPSERT/MAX, cursor thường và dictionary row.
- Thiếu game.db/schema: migration SQLite 005 tự khởi tạo, WAL/busy_timeout/foreign_keys, backup trước nâng phiên bản, không seed user.
- Browser Notebook mở DB local: data_provider API, dữ liệu JOIN từ server; phím N mở/ESC đóng, xem trước không hoàn thành quest.
- Browser fallback thiếu/khác ID: game/content cấp toàn bộ manh mối mọi sự kiện, chặn chơi online khi chưa có nội dung chính thức.
- Quest local completed trước response: task xác nhận, chỉ cập nhật điểm/completed sau server thành công.
- Footer deduction chồng chữ: bỏ footer timeline vẽ thêm từ main.
- Font Arial không có license phân phối: build dùng Noto Sans và OFL.

### Kiểm thử đã chạy thật
- pytest: 70 PASS, 0 FAIL, 0 SKIP; 7 subtest PASS. Một cảnh báo httpx/Starlette deprecation.
- Compile các module data/task3/task4/task5/scenes/services/main/web: PASS.
- SQLite file tạm: DB trống/DB cũ, backup, migration lặp, rollback sau INSERT bằng trigger lỗi,
  giữ bảng Task khác, giữ _task5, đăng nhập sai/đúng/không tồn tại, duplicate register,
  JWT invalid, role teacher/player, quiz concurrent, retry concurrent: PASS.
- Process mới đọc lại tiến độ SQLite: PASS.
- Pygbag build: PASS; ZIP không DB, .env, profile, seed hoặc server; Noto/OFL có, Arial không.
- Edge thật, không HTTP mock: register -> sai -> review +15 một lần -> quiz -> clues -> quest
  +30 một lần -> login/restore -> leaderboard PASS. Thao tác UI login/Notebook/Bảng Vàng và
  quest đầu với SQLite thật PASS, page_errors=[]. Một phần chuỗi sử dụng page.evaluate(fetch),
  không gọi đó là mọi thao tác UI end-to-end.
- Desktop SQLite thật file tạm: login screen/review/Notebook draw PASS.
- Docker: CHƯA KIỂM THỬ (không có Docker CLI), không giả PASS.

Bằng chứng: data/sqlite-browser-result.json, data/sqlite-notebook.png, data/sqlite-browser.png.
Chạy lại: python -m pytest -q tests; python -m task5.build_web;
python -m task5.check_sqlite_browser. Các DB/API test tự dừng, không dùng DB nhóm.

### Giới hạn
- Docker build/run/restart volume cần nghiệm thu trên máy có Docker.
- UI toàn bộ 11 địa điểm/timeline chưa chạy hết; bản seed gốc giữ 8 địa điểm/30 sự kiện/8 nhân vật/10 manh mối/8 câu hỏi, không tự bịa thêm.
- Không chứng minh người chơi đọc tư liệu; thời gian client có thể gian lận.
- Triển khai public cần hosting/persistent disk/HTTPS và JWT_SECRET thật. Chưa public.
- Nhật ký review offline và DB điểm là hai nơi lưu; không cam kết transaction phân tán/multi-device cho desktop. Online SQLite transaction là nguồn chuẩn.

File thay đổi chính: config.py, data/db_queries.py, data/sqlite_store.py, migration 005,
historical_seed.json/seed_source.md, task5/server/{repository,app}.py, api_game_data_service.py,
main.py/main_web.py, build_web.py/font_utils.py, task4/clue_notebook_scene.py (điểm nối nhỏ),
services/game_data_service.py, requirements, Dockerfile/ignore/env và tests SQLite/Notebook/quest.

## Lần nghiệm thu hiện tại — kết luận có điều kiện

Đã chạy lại, không chỉ lấy kết quả lịch sử:

| Hạng mục | Kết quả | Phạm vi bằng chứng |
|---|---|---|
| pytest | 57 test chính + 7 subtest đạt, mã thoát 0 | Unit, cursor giả, HTTP giả, UI surface |
| compileall | đạt, mã thoát 0 | Task 5, tests, main/web, login/review, data service |
| Build Pygbag sạch | đạt, mã thoát 0 | `build/web-source/build/web` |
| Edge thật mock-actions | ready=true, mock_login_pass=true, page_errors=[] | Login/review/retry/leaderboard HTTP giả |
| Desktop API-off | login/review step đạt, mã thoát 0 | Cache, DB connection bị chặn |
| Docker runtime | chưa nghiệm thu | Không phát hiện lệnh Docker |
| MySQL transaction/concurrency thật | chưa nghiệm thu | Không thực hiện ghi thử DB |
| Quest web end-to-end | chưa đạt đủ điều kiện nghiệm thu | main_web mới tải questions, chưa tải investigation_data/manh mối DB |

**Kết luận:** chấp nhận các thành phần trong phạm vi unit/mock và các smoke/E2E giả nêu trên; chưa chấp nhận toàn bộ Task 5 để public.

Các điểm chặn cần giải quyết tiếp:

1. Đồng bộ bộ manh mối DB về browser, không dùng ID cache khác ID server.
2. Test browser đầy đủ deduction/quiz -> lưu manh mối -> complete quest -> logout/login -> khôi phục điểm/tiến độ trên DB thử riêng.
3. Đối chiếu luồng complete local với server: local vẫn đánh dấu completed trước/không chờ xác nhận complete async, có thể lệch nếu server từ chối.
4. Thử migration, khóa và rollback/concurrency bằng MySQL/MariaDB riêng; không suy ra từ mock.
5. Docker, quyền phân phối font, khôi phục thưởng JSON/DB khi mất mạng chưa có nghiệm thu thực tế.

Cảnh báo còn lại khi chạy test: Starlette TestClient cảnh báo deprecation httpx. Không làm test thất bại, nhưng nên đồng bộ dependency trước release.

Kết quả browser mới được ghi tại `data/browser-check.json`; ảnh thật `data/browser-check.png`. Không cập nhật build cũ `.web-staging` và không public.

## Cập nhật chính sách tiến độ/quest server

- 57 test + 7 subtest đạt; compile/build sạch mã thoát 0; Edge mock-actions và desktop API-off tiếp tục đạt.
- Chính sách mở khóa đối chiếu trực tiếp QuestManager Task 4: địa điểm đầu chưa hoàn thành theo start và ngoại lệ Ba Đình mở Điện Biên Phủ. Không sửa Task 4.
- `/progress/save` không được tự thêm completed, chọn địa điểm khóa, ghi khóa `_task5` hoặc tăng quiz_attempts. ID manh mối phải thuộc DB địa điểm; hợp nhất dữ liệu hợp lệ, không ghi đè mất manh mối cũ.
- Năm lưu do server suy ra từ địa điểm đã mở; không tin năm 1975 do client tự khai.
- Complete quest kiểm tra địa điểm mở, đủ manh mối DB đã lưu và đủ quiz server trước khi thưởng. Khóa `_task5` bị lọc khỏi tiến độ trả về client.
- Browser POST được tuần tự hóa để lưu manh mối trước complete quest.
- Giới hạn: client vẫn tự gửi hành động thu thập ID hợp lệ, nên không chứng minh người chơi thực sự đọc/đối chiếu tư liệu. Chưa có MySQL transaction/concurrency E2E, và cache browser cần nạp đầy đủ dữ liệu manh mối DB để đồng nhất với ID server. Không gọi đây là bản public hoàn chỉnh.

## Cập nhật điểm nối deduction

- Game chặn/chấm đáp án deduction trước khi scene tiến câu; API lỗi không chuyển câu và không cộng local, kết quả server ưu tiên hơn cache, browser bấm lặp chỉ gửi một request.
- Mapping câu hỏi giữ ID DB và nguồn theo sự kiện; endpoint `/game/questions` cung cấp bộ câu có ID cho browser bằng fetch task riêng.
- Đã chuẩn hóa ID log để `042`/`42` không nhận điểm hai lần.
- Test mới cho mapping, lỗi mạng, cache sai, async duplicate và ID chuẩn. Không sửa source scene deduction thuộc task khác.
- Browser Edge login/review/retry/leaderboard HTTP giả tiếp tục đạt sau build. Chưa chứng minh toàn bộ deduction/quest/MySQL end-to-end.
- Quest vẫn chưa kiểm chứng manh mối và thứ tự mở khóa server-side; đó là hạng mục tiếp theo, không được coi đã nghiệm thu chỉ vì điểm nối deduction có test.

## Cập nhật mới nhất: hành động browser async

- 43 test chính + 7 subtest đạt; compile đạt; desktop API-off chạy login/review với DB bị chặn.
- Adapter đã có async quiz, retry, leaderboard, refresh review; save/quest dùng task nền fetch, có thu thập lỗi. Kết quả queued không có nghĩa server đã lưu.
- Game trì hoãn xử lý quiz browser đến khi response về, chặn bấm lặp; ReviewScene/LeaderboardScene poll task, không chặn frame.
- Response quiz/retry/review của phiên cũ bị từ chối sau logout; task nền bị hủy khi logout.
- Edge thật: `python -m task5.check_web_runtime --seconds 60 --mock-actions` đạt: login, review, retry, leaderboard đúng thứ tự, first-frame ready, không pageerror. HTTP giả bằng Playwright, không kết nối DB.
- Save và quiz có test async với transport giả; chưa nghiệm thu chuỗi chơi quiz/save với MySQL thật hoặc kiểm thử mạng đồng thời thực tế. Không công bố toàn bộ Task 5 hoàn tất.
- Build mới tại `build/web-source/build/web`. `.web-staging` cũ không tự cập nhật.

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