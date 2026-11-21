"""DAL SQLite dùng chung desktop/server. Không xác thực mật khẩu rõ hoặc REPLACE tiến độ."""
from __future__ import annotations
import json
import sqlite3
import bcrypt
from data.sqlite_store import connect


def get_db_connection():
    try:
        return connect(), 'OK'
    except Exception as exc:
        return None, str(exc)


def execute_select_query(sql, params=None):
    conn, message = get_db_connection()
    if conn is None:
        return None, message
    try:
        return conn.execute(sql, params or ()).fetchall(), 'OK'
    except sqlite3.Error as exc:
        return None, str(exc)
    finally:
        conn.close()


def fetch_raw_dia_diem(): return execute_select_query('SELECT * FROM dia_diem ORDER BY ma_dia_diem')
def fetch_raw_su_kien(): return execute_select_query('SELECT * FROM su_kien_lich_su ORDER BY ma_su_kien')
def fetch_raw_nhan_vat(): return execute_select_query('SELECT * FROM nhan_vat ORDER BY ma_nhan_vat')
def fetch_raw_manh_moi(): return execute_select_query('SELECT * FROM manh_moi ORDER BY ma_su_kien,ma_manh_moi')
def fetch_raw_cau_hoi(): return execute_select_query('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi')
def fetch_raw_nguoi_dung(): return execute_select_query('SELECT ma_nguoi_dung,ten_dang_nhap,ho_va_ten,vai_tro FROM nguoi_dung')


def authenticate_user(user, pwd):
    conn, message = get_db_connection()
    if conn is None: return None, message
    try:
        row = conn.execute('SELECT u.*,s.password_hash FROM nguoi_dung u LEFT JOIN tai_khoan_bao_mat s ON s.ma_nguoi_dung=u.ma_nguoi_dung WHERE ten_dang_nhap=?', (user,)).fetchone()
        if not row: return None, 'Sai tài khoản hoặc mật khẩu.'
        hashed = row.get('password_hash') or row.get('mat_khau_ma_hoa', '')
        # Legacy plaintext không được coi là đã xác thực; yêu cầu đặt lại mật khẩu.
        if not hashed.startswith(('$2a$', '$2b$', '$2y$')):
            return None, 'Tài khoản cũ cần đặt lại mật khẩu an toàn.'
        if not bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('ascii')):
            return None, 'Sai tài khoản hoặc mật khẩu.'
        return {k: row[k] for k in ('ma_nguoi_dung','ten_dang_nhap','ho_va_ten','vai_tro')}, 'OK'
    except (sqlite3.Error, ValueError, UnicodeError) as exc:
        return None, str(exc)
    finally:
        conn.close()


def register_user(user, pwd, name):
    conn, message = get_db_connection()
    if conn is None: return None, message
    try:
        if not user.strip() or len(pwd) < 8 or len(pwd.encode('utf-8')) > 72:
            return None, 'Mật khẩu cần ít nhất 8 ký tự và tối đa 72 byte UTF-8.'
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('ascii')
        conn.execute('BEGIN IMMEDIATE')
        cursor = conn.execute("INSERT INTO nguoi_dung(ten_dang_nhap,mat_khau_ma_hoa,ho_va_ten,vai_tro) VALUES(?,?,?,'player')", (user, hashed, name))
        uid = cursor.lastrowid
        conn.execute('INSERT INTO tai_khoan_bao_mat(ma_nguoi_dung,password_hash) VALUES(?,?)', (uid, hashed))
        conn.execute('INSERT INTO tien_do_choi(ma_nguoi_dung) VALUES(?)', (uid,))
        conn.commit()
        return {'ma_nguoi_dung':uid,'ten_dang_nhap':user,'ho_va_ten':name,'vai_tro':'player'}, 'OK'
    except (sqlite3.Error, ValueError) as exc:
        conn.rollback()
        return None, str(exc)
    finally: conn.close()


def fetch_user_progress(uid):
    rows, message = execute_select_query('SELECT * FROM tien_do_choi WHERE ma_nguoi_dung=?', (uid,))
    return (rows[0] if rows else None), message


def save_user_progress(uid, loc, year, score, locs, task_data=None):
    conn, message = get_db_connection()
    if conn is None: return False, message
    try:
        conn.execute('BEGIN IMMEDIATE')
        old = conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?', (uid,)).fetchone()
        state = json.loads(old.get('du_lieu_nhiem_vu') or '{}') if old else {}
        if task_data is not None:
            state.update(json.loads(task_data) if isinstance(task_data,str) else task_data)
        conn.execute('''INSERT INTO tien_do_choi(ma_nguoi_dung,ma_dia_diem_hien_tai,nam_mo_khoa_cao_nhat,diem_tri_thuc,danh_sach_dia_diem_da_mo,du_lieu_nhiem_vu)
          VALUES(?,?,?,?,?,?) ON CONFLICT(ma_nguoi_dung) DO UPDATE SET
          ma_dia_diem_hien_tai=excluded.ma_dia_diem_hien_tai, nam_mo_khoa_cao_nhat=MAX(tien_do_choi.nam_mo_khoa_cao_nhat,excluded.nam_mo_khoa_cao_nhat),
          diem_tri_thuc=excluded.diem_tri_thuc,danh_sach_dia_diem_da_mo=excluded.danh_sach_dia_diem_da_mo,du_lieu_nhiem_vu=excluded.du_lieu_nhiem_vu''',
          (uid,loc,year,max(0,int(score)),locs,json.dumps(state,ensure_ascii=False)))
        conn.commit(); return True,'Saved'
    except (sqlite3.Error, ValueError, TypeError) as exc:
        conn.rollback(); return False,str(exc)
    finally: conn.close()


def fetch_task4_progress(uid):
    row, message = fetch_user_progress(uid)
    if not row: return [],message
    try:
        state = json.loads(row.get('du_lieu_nhiem_vu') or '{}')
        return [{'ma_dia_diem':int(k),'clue_ids':json.dumps(v.get('clue_ids',[])), 'quiz_attempts':v.get('quiz_attempts',0)} for k,v in state.items() if k.isdigit() and isinstance(v,dict)],'OK'
    except (ValueError, TypeError): return [],'Dữ liệu nhiệm vụ không hợp lệ'


def save_task4_progress(uid, loc, clues, attempts):
    conn, message = get_db_connection()
    if conn is None: return False,message
    try:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()
        state = json.loads(row.get('du_lieu_nhiem_vu') or '{}') if row else {}
        previous = state.get(str(loc),{})
        ids = json.loads(clues) if isinstance(clues,str) else list(clues)
        state[str(loc)] = {'clue_ids':sorted(set(previous.get('clue_ids',[]))|set(ids)), 'quiz_attempts':max(int(attempts),int(previous.get('quiz_attempts',0)))}
        conn.execute('INSERT INTO tien_do_choi(ma_nguoi_dung,du_lieu_nhiem_vu) VALUES(?,?) ON CONFLICT(ma_nguoi_dung) DO UPDATE SET du_lieu_nhiem_vu=excluded.du_lieu_nhiem_vu',(uid,json.dumps(state,ensure_ascii=False)))
        conn.commit(); return True,'Saved'
    except (sqlite3.Error,ValueError,TypeError) as exc:
        conn.rollback(); return False,str(exc)
    finally: conn.close()