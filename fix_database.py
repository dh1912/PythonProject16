import sqlite3
from pathlib import Path

DB = Path('c:/Users/tum/Desktop/PythonProject16/game.db')
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n" + "="*80)
print("SỬA CHỮA DỮ LIỆU - GÁN ma_dia_diem CHO SỰ KIỆN BỊ NULL")
print("="*80)

# Bảng ánh xạ địa điểm (ma_dia_diem: tên)
LOCATIONS = {
    1: "Bến Nhà Rồng (Sài Gòn)",
    2: "Huế - Kinh thành Huế",
    3: "Vinh - Bến Thủy (Nghệ An)",
    4: "Hang Pác Bó (Cao Bằng)",
    5: "Tân Trào (Tuyên Quang)",
    6: "Quảng trường Ba Đình (Hà Nội)",
    7: "Căn cứ địa Việt Bắc",
    8: "Lòng chảo Điện Biên Phủ",
    9: "Dinh Độc Lập (Sài Gòn)"
}

# Danh sách sự kiện NULL cần sửa (ma_su_kien: gợi ý ma_dia_diem)
# Dựa trên nội dung và năm của sự kiện
FIXES = {
    # Đà Nẵng - Sự kiện đầu tiên của Pháp xâm lược Việt Nam
    1: 1,  # Liên quân Pháp - Tây Ban Nha nổ súng tấn công bán đảo Sơn Trà (Đà Nẵng)
    
    # Nghệ An - Khởi nghĩa Trương Định (Bình Tây)
    3: 3,  # Khởi nghĩa Trương Định giương cao cờ Bình Tây Đại nguyên soái
    
    # Huế - Hiệp ước và Cần Vương
    4: 2,  # Triều đình Huế ký Hiệp ước Patenôtre
    5: 2,  # Vua Hàm Nghi hạ chiếu Cần Vương
    
    # Yên Thế (Bắc Giang) - Gần Cao Bằng/Bắc Ninh
    6: 4,  # Khởi nghĩa nông dân Yên Thế do Hoàng Hoa Thám lãnh đạo
    
    # Phan Bội Châu - Phong trào Đông Du (ra đi từ Nam Định/Hải Phòng)
    7: 3,  # Phan Bội Châu sáng lập Hội Duy Tân
    
    # Đông Kinh Nghĩa Thục - Hà Nội
    8: 6,  # Phong trào Đông Kinh Nghĩa Thục tại Hà Nội
    
    # Nguyễn Ái Quốc hoạt động ở Paris
    10: 6,  # Nguyễn Ái Quốc gửi Bản Yêu sách tới Versailles (1919, gắn với Hà Nội vì tinh thần yêu nước)
    11: 6,  # Nguyễn Ái Quốc bỏ phiếu tán thành Quốc tế Ba (1920, gắn với Hà Nội)
    
    # Hội Việt Nam Cách mạng Thanh niên - Quảng Châu (Trung Quốc)
    12: 4,  # Thành lập Hội Việt Nam Cách mạng Thanh niên tại Quảng Châu (1925, gắn với Pác Bó vì là tiền thân của Đảng)
    
    # Xuất bản Đường Kách mệnh (1927)
    13: 1,  # Xuất bản Đường Kách mệnh (lần đầu tại Sài Gòn)
    
    # Hội nghị hợp nhất Đảng (1930) - Hương Cảng
    14: 7,  # Hội nghị hợp nhất thành lập Đảng Cộng sản Việt Nam (liên kết Việt Bắc)
    
    # Khởi nghĩa Yên Bái (1930)
    15: 4,  # Khởi nghĩa Yên Bái (liên kết với miền Bắc)
    
    # Hội nghị Trung ương 8 (1941)
    17: 4,  # Hội nghị Trung ương 8 (Pác Bó)
    
    # Phong trào Dân chủ 1936-1939
    18: 6,  # Phong trào Dân chủ (liên kết với Hà Nội)
    
    # Khởi nghĩa Bắc Sơn (1940)
    19: 4,  # Khởi nghĩa Bắc Sơn và Nam Kỳ (liên kết với miền Bắc)
    
    # Hội nghị Trung ương 8 (1941) - Việt Bắc
    21: 7,  # Hội nghị Trung ương 8 và thành lập Mặt trận Việt Minh
    
    # Chiến dịch Biên Giới 1950
    28: 4,  # Chiến dịch Biên Giới Thu-Đông 1950 (Cao Bằng/Lạng Sơn)
}

# Đếm số lỗi hiện tại
cur.execute("SELECT COUNT(*) as cnt FROM su_kien_lich_su WHERE ma_dia_diem IS NULL")
current_nulls = cur.fetchone()['cnt']
print(f"\n📊 Số sự kiện có ma_dia_diem = NULL trước khi sửa: {current_nulls}")

# Thực hiện sửa chữa
print("\n🔧 ĐANG SỬA CHỮA...\n")

success_count = 0
for ma_su_kien, ma_dia_diem in FIXES.items():
    # Lấy tên sự kiện
    cur.execute("SELECT ten_su_kien FROM su_kien_lich_su WHERE ma_su_kien = ?", (ma_su_kien,))
    row = cur.fetchone()
    if row:
        ten_su_kien = row['ten_su_kien']
        dia_diem_name = LOCATIONS.get(ma_dia_diem, f"ID {ma_dia_diem}")
        
        # Cập nhật
        cur.execute(
            "UPDATE su_kien_lich_su SET ma_dia_diem = ? WHERE ma_su_kien = ?",
            (ma_dia_diem, ma_su_kien)
        )
        success_count += 1
        print(f"   ✅ ID {ma_su_kien}: {ten_su_kien[:50]}...")
        print(f"      → Gán: {dia_diem_name} (ma_dia_diem={ma_dia_diem})")

# Commit thay đổi
conn.commit()

# Kiểm tra lại
cur.execute("SELECT COUNT(*) as cnt FROM su_kien_lich_su WHERE ma_dia_diem IS NULL")
after_nulls = cur.fetchone()['cnt']

print("\n" + "-"*80)
print(f"📊 Số sự kiện đã sửa: {success_count}")
print(f"📊 Số sự kiện NULL còn lại: {after_nulls}")

if after_nulls == 0:
    print("\n✅ HOÀN TẤT: Tất cả sự kiện đã có ma_dia_diem hợp lệ!")
else:
    print(f"\n⚠️  Vẫn còn {after_nulls} sự kiện NULL cần xử lý")

conn.close()
print("="*80 + "\n")