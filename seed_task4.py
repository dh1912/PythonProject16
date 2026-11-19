"""Script nạp và đồng bộ toàn bộ dữ liệu CSDL phục vụ Task 4 vào MySQL XAMPP."""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from data.db_queries import get_db_connection


def apply_task4_migration():
    print(">> Đang kết nối MySQL XAMPP và nạp dữ liệu Task 4...")
    conn, status = get_db_connection()
    if not conn:
        print(f"[THẤT BẠI] {status}")
        return False

    migration_path = os.path.join(CURRENT_DIR, "data", "migrations", "004_task4_complete.sql")
    if not os.path.exists(migration_path):
        print(f"[LỖI] Không tìm thấy file migration tại: {migration_path}")
        return False

    with open(migration_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Tách từng câu lệnh SQL bởi dấu chấm phẩy
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip() and not stmt.strip().startswith("--")]

    success_count = 0
    with conn.cursor() as cursor:
        for stmt in statements:
            try:
                cursor.execute(stmt)
                success_count += 1
            except Exception as e:
                # Bỏ qua nếu lệnh USE game hoặc cột đã tồn tại
                if "USE" in stmt.upper():
                    continue
                print(f"  [Lưu ý SQL] {e}")

    conn.commit()
    conn.close()
    print(f"✓ THÀNH CÔNG: Đã thực thi {success_count} câu lệnh nâng cấp dữ liệu cho Task 4!")
    return True


if __name__ == "__main__":
    apply_task4_migration()
