import sqlite3

def cleanup_database():
    conn = sqlite3.connect('c:/Users/tum/Desktop/PythonProject16/game.db')
    cursor = conn.cursor()
    
    # Các bảng cần xóa (thừa/rác)
    tables_to_drop = ['sqlite_sequence', 'su_kien_30', 'nhan_vat_lich_su', 'tui_do_nguoi_choi']
    
    print("=== XÓA CÁC BẢNG THỪA/RÁC ===")
    for t in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS \"{t}\"")
            print(f"  ✓ Đã xóa bảng: {t}")
        except Exception as e:
            print(f"  ✗ Lỗi xóa {t}: {e}")
    
    conn.commit()
    
    # Kiểm tra lại danh sách bảng
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"\n=== DANH SÁCH BẢNG SAU KHI DỌN DẸP: {tables} ===")
    
    # Hiển thị số bản ghi các bảng còn lại
    print("\n=== SỐ BẢN GHI CÁC BẢNG ===")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM \"{t}\"")
        cnt = cursor.fetchone()[0]
        print(f"  - {t}: {cnt} bản ghi")
    
    conn.close()
    print("\n✓ Hoàn tất dọn dẹp database!")

if __name__ == '__main__':
    cleanup_database()