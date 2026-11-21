import sqlite3
from pathlib import Path

DB = Path("c:/Users/tum/Desktop/PythonProject16/game.db")

def conn():
    c = sqlite3.connect(str(DB))
    c.row_factory = sqlite3.Row
    return c

def view(table):
    c = conn()
    cur = c.cursor()
    cur.execute(f"SELECT * FROM \"{table}\"")
    rows = cur.fetchall()
    print(f"\n=== {table} ({len(rows)} dong) ===")
    for r in rows:
        print(dict(r))
    c.close()

def add_user(u, p, n, r="player"):
    c = conn()
    try:
        c.execute("INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_ma_hoa, ho_va_ten, vai_tro) VALUES (?,?,?,?)", (u,p,n,r))
        c.commit()
        print(f"OK: {u}")
    except Exception as e:
        print(f"Loi: {e}")
    finally:
        c.close()

def update_user(uid, **kw):
    c = conn()
    try:
        cols = ", ".join([f"{k}=?" for k in kw])
        vals = list(kw.values()) + [uid]
        c.execute(f"UPDATE nguoi_dung SET {cols} WHERE ma_nguoi_dung=?", vals)
        c.commit()
        print(f"OK: User {uid}")
    except Exception as e:
        print(f"Loi: {e}")
    finally:
        c.close()

def delete_user(uid):
    c = conn()
    try:
        c.execute("DELETE FROM nguoi_dung WHERE ma_nguoi_dung=?", (uid,))
        c.commit()
        print(f"OK: Deleted {uid}")
    except Exception as e:
        print(f"Loi: {e}")
    finally:
        c.close()

def update_progress(uid, loc, year, score):
    c = conn()
    try:
        c.execute("INSERT OR REPLACE INTO tien_do_choi (ma_nguoi_dung, ma_dia_diem_hien_tai, nam_mo_khoa_cao_nhat, diem_tri_thuc) VALUES (?,?,?,?)", (uid,loc,year,score))
        c.commit()
        print(f"OK: Progress {uid}")
    except Exception as e:
        print(f"Loi: {e}")
    finally:
        c.close()

def menu():
    while True:
        print("\n=== QUAN LY game.db ===")
        print("1. Xem bang\n2. Them user\n3. Sua user\n4. Xoa user\n5. Cap nhat tien do\n0. Thoat")
        c = input("Chon: ").strip()
        if c == "1":
            t = input("Bang (nguoi_dung, dia_diem, ...): ")
            view(t)
        elif c == "2":
            add_user(input("User: "), input("Pass: "), input("Name: "))
        elif c == "3":
            update_user(int(input("ID: ")), **{input("Field: "): input("Value: ")})
        elif c == "4":
            delete_user(int(input("ID: ")))
        elif c == "5":
            update_progress(int(input("ID: ")), int(input("Loc: ")), int(input("Year: ")), int(input("Score: ")))
        elif c == "0":
            break

menu()
