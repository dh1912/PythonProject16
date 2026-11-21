"""
================================================================================
HƯỚNG DẪN ĐỒ SỌ VÀ NỐI DỮ LIỆU LIÊN KẾT - GAME.DB
================================================================================

📋 SƠ ĐỒ QUAN HỆ DỮ LIỆU:

nguoi_dung (5 người dùng)
    │
    ├── tien_do_choi (4 tiến độ)
    │   └── dia_diem (9 địa điểm)
    │
    └── tui_do_nguoi_choi (túi đồ)

dia_diem (9 địa điểm)
    │
    ├── su_kien_lich_su (30 sự kiện)
    │   ├── manh_moi (36 manh mối)
    │   ├── cau_hoi_on_tap (30 câu hỏi)
    │   ├── moc_lich_su (30 mốc thời gian)
    │   └── nguon_lich_su (30 nguồn)
    │
    └── nhan_vat (8 nhân vật)
        └── manh_moi (36 manh mối)

================================================================================
"""

import sqlite3
from pathlib import Path

DB = Path('c:/Users/tum/Desktop/PythonProject16/game.db')

def connect():
    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA foreign_keys = ON")
    c.row_factory = sqlite3.Row
    return c

# Kiểm tra liên kết dữ liệu
def check_sync():
    c = connect()
    cur = c.cursor()
    
    print("\n" + "="*70)
    print("KIỂM TRA ĐỒNG BỘ & LIÊN KẾT DỮ LIỆU")
    print("="*70)
    
    checks = [
        ("su_kien_lich_su → dia_diem",
         "SELECT COUNT(*) FROM su_kien_lich_su WHERE ma_dia_diem NOT IN (SELECT ma_dia_diem FROM dia_diem) AND ma_dia_diem IS NOT NULL"),
        
        ("nhan_vat → dia_diem",
         "SELECT COUNT(*) FROM nhan_vat WHERE ma_dia_diem NOT IN (SELECT ma_dia_diem FROM dia_diem) AND ma_dia_diem IS NOT NULL"),
        
        ("manh_moi → su_kien_lich_su",
         "SELECT COUNT(*) FROM manh_moi WHERE ma_su_kien NOT IN (SELECT ma_su_kien FROM su_kien_lich_su) AND ma_su_kien IS NOT NULL"),
        
        ("manh_moi → nhan_vat",
         "SELECT COUNT(*) FROM manh_moi WHERE ma_nhan_vat NOT IN (SELECT ma_nhan_vat FROM nhan_vat) AND ma_nhan_vat IS NOT NULL"),
        
        ("cau_hoi_on_tap → su_kien_lich_su",
         "SELECT COUNT(*) FROM cau_hoi_on_tap WHERE ma_su_kien NOT IN (SELECT ma_su_kien FROM su_kien_lich_su) AND ma_su_kien IS NOT NULL"),
        
        ("tien_do_choi → nguoi_dung",
         "SELECT COUNT(*) FROM tien_do_choi WHERE ma_nguoi_dung NOT IN (SELECT ma_nguoi_dung FROM nguoi_dung) AND ma_nguoi_dung IS NOT NULL"),
        
        ("tien_do_choi → dia_diem",
         "SELECT COUNT(*) FROM tien_do_choi WHERE ma_dia_diem_hien_tai NOT IN (SELECT ma_dia_diem FROM dia_diem) AND ma_dia_diem_hien_tai IS NOT NULL"),
    ]
    
    errors = 0
    for name, sql in checks:
        cur.execute(sql)
        bad = cur.fetchone()[0]
        if bad > 0:
            print(f"❌ {name:35} - {bad} lỗi")
            errors += 1
        else:
            print(f"✅ {name:35} - OK")
    
    c.close()
    
    print("\n" + "="*70)
    if errors == 0:
        print("✅ TẤT CẢ LIÊN KẾT ĐÚNG - DỮ LIỆU ĐỒNG BỘ!")
    else:
        print(f"⚠️  CÓ {errors} LIÊN KẾT CÓ LỖI - CẦN SỬA CHỮA!")
    print("="*70 + "\n")
    
    return errors == 0

if __name__ == '__main__':
    check_sync()
