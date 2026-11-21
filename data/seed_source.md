# Nguồn seed SQLite

historical_seed.json chỉ chứa 5 bảng nội dung, trích từ game.sql tại commit
c7813c3 đã có trong lịch sử repository (không có tài khoản hoặc tiến độ).
Giữ nguyên ID và liên kết lịch sử của dump; không tự gán lại địa điểm cho sự kiện.
Các cột nguồn lịch sử bổ sung không nằm trong schema tối thiểu không được tự suy diễn.
Migration chỉ INSERT ... ON CONFLICT DO NOTHING, không ghi đè dữ liệu hiện có.