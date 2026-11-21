import sqlite3, json, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB_PATH = PROJECT_ROOT / "game.db"

def get_db_connection():
    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn, "OK"
    except Exception as e:
        return None, str(e)

def execute_select_query(sql, params=None):
    conn, status = get_db_connection()
    if not conn: return None, status
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return [dict(r) for r in rows] if rows else [], status
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def fetch_raw_dia_diem():
    return execute_select_query("SELECT * FROM dia_diem ORDER BY ma_dia_diem")

def fetch_raw_su_kien():
    return execute_select_query("SELECT * FROM su_kien_lich_su ORDER BY ma_su_kien")

def fetch_raw_nhan_vat():
    return execute_select_query("SELECT * FROM nhan_vat ORDER BY ma_nhan_vat")

def fetch_raw_manh_moi():
    return execute_select_query("SELECT * FROM manh_moi ORDER BY ma_su_kien")

def fetch_raw_cau_hoi():
    return execute_select_query("SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi")

def fetch_raw_nguoi_dung():
    return execute_select_query("SELECT * FROM nguoi_dung")

def authenticate_user(user, pwd):
    conn, status = get_db_connection()
    if not conn: return None, status
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ?", (user,))
        row = cursor.fetchone()
        return (dict(row), "OK") if row else (None, "Not found")
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def register_user(user, pwd, name):
    conn, status = get_db_connection()
    if not conn: return None, status
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_ma_hoa, ho_va_ten, vai_tro) VALUES (?,?,?,?)", (user, pwd, name, "player"))
        conn.commit()
        cursor.execute("SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ?", (user,))
        row = cursor.fetchone()
        return (dict(row), "OK") if row else (None, "Error")
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def fetch_user_progress(uid):
    conn, status = get_db_connection()
    if not conn: return None, status
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tien_do_choi WHERE ma_nguoi_dung = ?", (uid,))
        row = cursor.fetchone()
        return (dict(row), "OK") if row else (None, "No data")
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def save_user_progress(uid, loc, year, score, locs, task_data=None):
    conn, status = get_db_connection()
    if not conn: return False, status
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO tien_do_choi (ma_nguoi_dung, ma_dia_diem_hien_tai, nam_mo_khoa_cao_nhat, diem_tri_thuc, danh_sach_dia_diem_da_mo, du_lieu_nhiem_vu) VALUES (?,?,?,?,?,?)", (uid, loc, year, score, locs, task_data))
        conn.commit()
        return True, "Saved"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def fetch_task4_progress(uid):
    conn, status = get_db_connection()
    if not conn: return [], status
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung = ?", (uid,))
        row = cursor.fetchone()
        if not row or not row["du_lieu_nhiem_vu"]: return [], "No data"
        raw = json.loads(row["du_lieu_nhiem_vu"])
        rows = []
        for k, v in raw.items():
            try:
                rows.append({"ma_dia_diem": int(k), "clue_ids": json.dumps(v.get("clue_ids", [])), "quiz_attempts": v.get("quiz_attempts", 0)})
            except: pass
        return rows, "OK"
    except Exception as e:
        return [], str(e)
    finally:
        conn.close()

def save_task4_progress(uid, loc, clues, attempts):
    conn, status = get_db_connection()
    if not conn: return False, status
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung = ?", (uid,))
        row = cursor.fetchone()
        current_data = {}
        if row and row["du_lieu_nhiem_vu"]:
            try:
                current_data = json.loads(row["du_lieu_nhiem_vu"])
            except: pass
        try:
            c_ids = json.loads(clues) if isinstance(clues, str) else list(clues)
        except:
            c_ids = []
        current_data[str(loc)] = {"clue_ids": c_ids, "quiz_attempts": int(attempts)}
        cursor.execute("UPDATE tien_do_choi SET du_lieu_nhiem_vu = ? WHERE ma_nguoi_dung = ?", (json.dumps(current_data), uid))
        conn.commit()
        return True, "Saved"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
