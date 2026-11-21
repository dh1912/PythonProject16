# Biên bản nghiệm thu Task 5 trên workspace hiện tại

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