# Kiến trúc dự án

## Điểm vào chính

- `main.py`: game desktop Pygame, scene director và canvas HD `1280x720`.
- `main_web.py`: entry point Pygbag/WASM; không truy cập SQLite local trong browser.
- `task5.server.app`: FastAPI production cho đăng nhập, chấm điểm và lưu tiến độ.
- `task5.build_web`: staging source sạch trước khi build web.

## Tầng mã nguồn

```text
config.py                     cấu hình dùng chung
main.py / main_web.py         điều phối vòng đời và scene
scenes/                       UI/gameplay scene lõi
services/                     adapter dữ liệu desktop/API
 task4/                       quest, clue, timeline, notebook, inventory/review UI
 task5/                       review, scoring, settings, leaderboard, server
 task1/ / task3/               API và đồ thị lịch sử độc lập
data/                         schema, migration, seed nội dung lịch sử
tests/                        regression/unit/integration test
```

## Quy tắc phụ thuộc

1. `main.py` điều phối scene; scene không tự khởi động server hoặc tạo database.
2. `services/` là lớp duy nhất chọn desktop cache hay API online.
3. `task4` và `task5` chứa domain/UI chuyên biệt; không import ngược `main.py`.
4. Server chỉ nhận dữ liệu đã validate; không dùng Pygame.
5. Browser build dùng `main_web.py` và allowlist của `task5.build_web`; không đóng gói DB,
   secret, review local hoặc server test.
6. Canvas logic chuẩn là `1280x720`; scene tự wrap/clip nội dung dài, không kéo giãn chữ
   theo từng trục.

## Artifact và file cục bộ

Các mục sau không phải source runtime và không commit:

- `__pycache__/`, `.pytest_cache/`, `build/`, `dist/`, `.web-staging/`.
- `*.log`, file chẩn đoán UI, ảnh snapshot sinh bởi acceptance.
- `*.db-wal`, `*.db-shm`, backup DB cục bộ và review progress cá nhân.

Giữ lại các tài nguyên nghiệp vụ được runtime tham chiếu như `assets/`, `bando.jpg`,
`data/historical_*.json`, migration và `game.db` local của môi trường phát triển.
Không xóa thư mục dữ liệu chưa xác minh nguồn gốc; kiểm tra import/manifest trước khi dọn.

## Kiểm tra trước khi merge

```powershell
python -m pytest -q tests
python -m compileall -q data task5 task3 task4 scenes services main.py main_web.py
python -m task5.build_web --stage-only
```
