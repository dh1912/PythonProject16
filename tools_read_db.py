"""Bộ công cụ CLI tra cứu, đọc và kiểm tra toàn bộ CSDL Game Lịch Sử Việt Nam."""
import sys
import pymysql

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def connect():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='game',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def show_summary():
    conn = connect()
    c = conn.cursor()
    print("=" * 65)
    print(">> TỔNG QUAN CƠ SỞ DỮ LIỆU GAME LỊCH SỬ VIỆT NAM (1858 - 1975)")
    print("=" * 65)
    tables = [
        ("dia_diem", "Cứ điểm lịch sử thuần Việt trên bản đồ"),
        ("su_kien_lich_su", "Sự kiện lịch sử dân tộc (1858 - 1975)"),
        ("manh_moi", "Manh mối hiện vật/văn kiện (Task 4)"),
        ("cau_hoi_on_tap", "Câu hỏi trắc nghiệm kiểm chứng (Task 4/5)"),
        ("nhan_vat_lich_su", "Danh nhân, nhân chứng lịch sử"),
        ("nguon_lich_su", "Nguồn sách, văn kiện học thuật cấp quốc gia"),
    ]
    for tbl, desc in tables:
        c.execute(f"SELECT COUNT(*) as total FROM {tbl}")
        cnt = c.fetchone()["total"]
        print(f"  * Bảng {tbl:18s}: {cnt:2d} dòng | {desc}")
    conn.close()


def show_locations():
    conn = connect()
    c = conn.cursor()
    print("\n" + "=" * 65)
    print(">> DANH SÁCH 9 ĐỊA DANH LỊCH SỬ TRÊN BẢN ĐỒ VIỆT NAM")
    print("=" * 65)
    c.execute("SELECT ma_dia_diem, ten_dia_diem, khu_vuc, toa_do_x, toa_do_y FROM dia_diem ORDER BY ma_dia_diem")
    for r in c.fetchall():
        print(f"[{r['ma_dia_diem']}] {r['ten_dia_diem']} (Miền {r['khu_vuc']}) -> Tọa độ: ({r['toa_do_x']}, {r['toa_do_y']})")
    conn.close()


def show_quest_data(loc_id=None):
    conn = connect()
    c = conn.cursor()
    print("\n" + "=" * 65)
    print(">> LIÊN KẾT NHÂN - QUẢ: MANH MỐI & TRẮC NGHIỆM TASK 4")
    print("=" * 65)
    sql = """
    SELECT d.ma_dia_diem, d.ten_dia_diem, s.ma_su_kien, s.ten_su_kien, s.nam_dien_ra
    FROM dia_diem d
    JOIN su_kien_lich_su s ON d.ma_dia_diem = s.ma_dia_diem
    """
    if loc_id:
        sql += f" WHERE d.ma_dia_diem = {loc_id}"
    sql += " ORDER BY d.ma_dia_diem"
    c.execute(sql)
    locations = c.fetchall()

    for loc in locations:
        print(f"\n--- ĐỊA DANH [{loc['ma_dia_diem']}]: {loc['ten_dia_diem']} ---")
        print(f"Sự kiện trung tâm: [{loc['nam_dien_ra']}] {loc['ten_su_kien']}")

        # Lấy 4 manh mối
        c.execute("""
            SELECT thu_tu_timeline_dung, loai_manh_moi, tieu_de_manh_moi, noi_dung_chi_tiet
            FROM manh_moi
            WHERE ma_su_kien = %s
            ORDER BY thu_tu_timeline_dung
        """, (loc['ma_su_kien'],))
        clues = c.fetchall()
        print("  * 4 Giai đoạn Timeline nhân - quả:")
        for cl in clues:
            print(f"    [{cl['thu_tu_timeline_dung']}] ({cl['loai_manh_moi']}) {cl['tieu_de_manh_moi']}")

        # Lấy 3 câu hỏi
        c.execute("""
            SELECT noi_dung_cau_hoi, dap_an_a, dap_an_b, dap_an_c, dap_an_d, dap_an_dung
            FROM cau_hoi_on_tap
            WHERE ma_su_kien = %s
        """, (loc['ma_su_kien'],))
        questions = c.fetchall()
        print("  * 3 Câu hỏi trắc nghiệm kiểm chứng:")
        for idx, q in enumerate(questions, 1):
            print(f"    Q{idx}: {q['noi_dung_cau_hoi']} (Đáp án: {q['dap_an_dung']})")

    conn.close()


if __name__ == "__main__":
    show_summary()
    show_locations()
    show_quest_data()
