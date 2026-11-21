import sqlite3
from pathlib import Path

DB = Path('c:/Users/tum/Desktop/PythonProject16/game.db')
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n" + "="*80)
print("KIỂM TRA TÍNH TOÀN VẸN DỮ LIỆU - game.db")
print("="*80)

# 1. Kiểm tra su_kien_lich_su
print("\n1. KIỂM TRA: su_kien_lich_su")
print("-" * 80)

cur.execute("SELECT COUNT(*) as cnt FROM su_kien_lich_su WHERE ma_dia_diem IS NULL")
null_count = cur.fetchone()['cnt']
print(f"   Sự kiện có ma_dia_diem = NULL: {null_count}")

if null_count > 0:
    cur.execute("SELECT ma_su_kien, ten_su_kien, ma_dia_diem FROM su_kien_lich_su WHERE ma_dia_diem IS NULL")
    for row in cur.fetchall():
        print(f"     ❌ ID {row['ma_su_kien']}: {row['ten_su_kien']}")

cur.execute("""
    SELECT COUNT(*) as cnt FROM su_kien_lich_su sk 
    WHERE sk.ma_dia_diem NOT IN (SELECT ma_dia_diem FROM dia_diem) 
    AND sk.ma_dia_diem IS NOT NULL
""")
invalid_count = cur.fetchone()['cnt']
print(f"   Sự kiện có ma_dia_diem không tồn tại: {invalid_count}")

if invalid_count > 0:
    cur.execute("""
        SELECT sk.ma_su_kien, sk.ten_su_kien, sk.ma_dia_diem FROM su_kien_lich_su sk 
        WHERE sk.ma_dia_diem NOT IN (SELECT ma_dia_diem FROM dia_diem) 
        AND sk.ma_dia_diem IS NOT NULL
    """)
    for row in cur.fetchall():
        print(f"     ❌ ID {row['ma_su_kien']}: {row['ten_su_kien']} (ma_dia_diem={row['ma_dia_diem']})")

print(f"   Tổng sự kiện hợp lệ: {30 - null_count - invalid_count}/30 ✓")

# 2. Kiểm tra manh_moi
print("\n2. KIỂM TRA: manh_moi")
print("-" * 80)

cur.execute("SELECT COUNT(*) as cnt FROM manh_moi WHERE ma_su_kien IS NULL")
null_count = cur.fetchone()['cnt']
print(f"   Manh mối có ma_su_kien = NULL: {null_count}")

if null_count > 0:
    cur.execute("SELECT ma_manh_moi, tieu_de_manh_moi FROM manh_moi WHERE ma_su_kien IS NULL")
    for row in cur.fetchall():
        print(f"     ❌ ID {row['ma_manh_moi']}: {row['tieu_de_manh_moi']}")

cur.execute("""
    SELECT COUNT(*) as cnt FROM manh_moi mm 
    WHERE mm.ma_su_kien NOT IN (SELECT ma_su_kien FROM su_kien_lich_su) 
    AND mm.ma_su_kien IS NOT NULL
""")
invalid_count = cur.fetchone()['cnt']
print(f"   Manh mối có ma_su_kien không tồn tại: {invalid_count}")

print(f"   Tổng manh mối hợp lệ: {36 - null_count - invalid_count}/36 ✓")

# 3. Kiểm tra cau_hoi_on_tap
print("\n3. KIỂM TRA: cau_hoi_on_tap")
print("-" * 80)

cur.execute("SELECT COUNT(*) as cnt FROM cau_hoi_on_tap WHERE ma_su_kien IS NULL")
null_count = cur.fetchone()['cnt']
print(f"   Câu hỏi có ma_su_kien = NULL: {null_count}")

if null_count > 0:
    cur.execute("SELECT ma_cau_hoi, noi_dung_cau_hoi FROM cau_hoi_on_tap WHERE ma_su_kien IS NULL")
    for row in cur.fetchall():
        print(f"     ❌ ID {row['ma_cau_hoi']}: {row['noi_dung_cau_hoi'][:50]}...")

cur.execute("""
    SELECT COUNT(*) as cnt FROM cau_hoi_on_tap ch 
    WHERE ch.ma_su_kien NOT IN (SELECT ma_su_kien FROM su_kien_lich_su) 
    AND ch.ma_su_kien IS NOT NULL
""")
invalid_count = cur.fetchone()['cnt']
print(f"   Câu hỏi có ma_su_kien không tồn tại: {invalid_count}")

print(f"   Tổng câu hỏi hợp lệ: {30 - null_count - invalid_count}/30 ✓")

# 4. Kiểm tra nhan_vat
print("\n4. KIỂM TRA: nhan_vat")
print("-" * 80)

cur.execute("SELECT COUNT(*) as cnt FROM nhan_vat WHERE ma_dia_diem IS NULL")
null_count = cur.fetchone()['cnt']
print(f"   Nhân vật có ma_dia_diem = NULL: {null_count}")

if null_count > 0:
    cur.execute("SELECT ma_nhan_vat, ten_nhan_vat FROM nhan_vat WHERE ma_dia_diem IS NULL")
    for row in cur.fetchall():
        print(f"     ❌ ID {row['ma_nhan_vat']}: {row['ten_nhan_vat']}")

cur.execute("""
    SELECT COUNT(*) as cnt FROM nhan_vat nv 
    WHERE nv.ma_dia_diem NOT IN (SELECT ma_dia_diem FROM dia_diem) 
    AND nv.ma_dia_diem IS NOT NULL
""")
invalid_count = cur.fetchone()['cnt']
print(f"   Nhân vật có ma_dia_diem không tồn tại: {invalid_count}")

print(f"   Tổng nhân vật hợp lệ: {8 - null_count - invalid_count}/8 ✓")

# 5. Thống kê sự kiện theo địa điểm
print("\n5. THỐNG KÊ: Sự kiện theo địa điểm")
print("-" * 80)

cur.execute("""
    SELECT dd.ma_dia_diem, dd.ten_dia_diem, COUNT(sk.ma_su_kien) as so_su_kien
    FROM dia_diem dd
    LEFT JOIN su_kien_lich_su sk ON dd.ma_dia_diem = sk.ma_dia_diem
    GROUP BY dd.ma_dia_diem
    ORDER BY so_su_kien DESC
""")

for row in cur.fetchall():
    print(f"   Địa điểm {row['ma_dia_diem']}: {row['ten_dia_diem']:30} → {row['so_su_kien']} sự kiện")

conn.close()
print("\n" + "="*80)
print("KIỂM TRA HOÀN THÀNH")
print("="*80 + "\n")
