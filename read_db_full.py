"""Doc toan bo du lieu database va kiem tra tinh trang cho du an."""
import pymysql

def get_conn():
    return pymysql.connect(host='localhost', user='root', password='',
        database='game', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

def doc_dia_diem(cursor):
    cursor.execute('SELECT ma_dia_diem, ten_dia_diem, khu_vuc, toa_do_x, toa_do_y FROM dia_diem ORDER BY ma_dia_diem')
    rows = cursor.fetchall()
    print(f"\n{'='*60}\nBANG DIA_DIEM: {len(rows)} dia diem\n{'='*60}")
    for d in rows:
        print(f"  [{d['ma_dia_diem']}] {d['ten_dia_diem']} | {d['khu_vuc']} | ({d['toa_do_x']},{d['toa_do_y']})")
    return rows

def doc_su_kien(cursor):
    cursor.execute('''SELECT s.ma_su_kien, s.ma_dia_diem, d.ten_dia_diem,
        s.ten_su_kien, s.nam_dien_ra
        FROM su_kien_lich_su s JOIN dia_diem d ON s.ma_dia_diem=d.ma_dia_diem
        ORDER BY s.ma_dia_diem, s.nam_dien_ra''')
    rows = cursor.fetchall()
    print(f"\n{'='*60}\nBANG SU_KIEN ({len(rows)} su kien):\n{'='*60}")
    hien_tai = None
    for s in rows:
        if s['ma_dia_diem'] != hien_tai:
            hien_tai = s['ma_dia_diem']
            print(f"\n  [DD{s['ma_dia_diem']}] {s['ten_dia_diem']}:")
        print(f"    -> [SK{s['ma_su_kien']}] {s['nam_dien_ra']}: {s['ten_su_kien']}")
    return rows

def doc_manh_moi(cursor):
    cursor.execute('''SELECT m.ma_manh_moi, m.ma_su_kien, s.ma_dia_diem,
        d.ten_dia_diem, m.tieu_de_manh_moi, m.loai_manh_moi,
        m.thu_tu_timeline_dung, m.noi_dung_chi_tiet
        FROM manh_moi m
        JOIN su_kien_lich_su s ON m.ma_su_kien=s.ma_su_kien
        JOIN dia_diem d ON s.ma_dia_diem=d.ma_dia_diem
        ORDER BY s.ma_dia_diem, m.thu_tu_timeline_dung''')
    rows = cursor.fetchall()
    print(f"\n{'='*60}\nBANG MANH_MOI ({len(rows)} manh moi):\n{'='*60}")
    hien_tai = None
    for m in rows:
        if m['ma_dia_diem'] != hien_tai:
            hien_tai = m['ma_dia_diem']
            print(f"\n  [DD{m['ma_dia_diem']}] {m['ten_dia_diem']}:")
        noi_dung = m['noi_dung_chi_tiet'][:70] if m['noi_dung_chi_tiet'] else ''
        print(f"    [stage{m['thu_tu_timeline_dung']}] ({m['loai_manh_moi']}) {m['tieu_de_manh_moi']}")
        print(f"           {noi_dung}...")
    return rows

def doc_cau_hoi(cursor):
    cursor.execute('''SELECT c.ma_cau_hoi, c.ma_su_kien, s.ma_dia_diem,
        d.ten_dia_diem, c.noi_dung_cau_hoi,
        c.dap_an_a, c.dap_an_b, c.dap_an_c, c.dap_an_d,
        c.dap_an_dung, c.giai_thich_chi_tiet
        FROM cau_hoi_on_tap c
        JOIN su_kien_lich_su s ON c.ma_su_kien=s.ma_su_kien
        JOIN dia_diem d ON s.ma_dia_diem=d.ma_dia_diem
        ORDER BY s.ma_dia_diem, c.ma_cau_hoi''')
    rows = cursor.fetchall()
    print(f"\n{'='*60}\nBANG CAU_HOI ({len(rows)} cau hoi):\n{'='*60}")
    hien_tai = None
    for c in rows:
        if c['ma_dia_diem'] != hien_tai:
            hien_tai = c['ma_dia_diem']
            print(f"\n  [DD{c['ma_dia_diem']}] {c['ten_dia_diem']}:")
        print(f"    [{c['dap_an_dung']}] {c['noi_dung_cau_hoi']}")
        print(f"         A: {c['dap_an_a']}")
        print(f"         B: {c['dap_an_b']}")
        print(f"         C: {c['dap_an_c']}")
        print(f"         D: {c['dap_an_d']}")
        gt = c['giai_thich_chi_tiet'][:80] if c['giai_thich_chi_tiet'] else ''
        print(f"         Giai thich: {gt}")
    return rows

def tong_ket(dia_diems, manh_mois, cau_hois):
    print(f"\n{'='*60}\nTONG KET & PHAT HIEN VAN DE:\n{'='*60}")
    # Thong ke theo dia diem
    count_mm = {}
    for m in manh_mois:
        did = m['ma_dia_diem']
        if did not in count_mm:
            count_mm[did] = []
        count_mm[did].append(m['thu_tu_timeline_dung'])
    count_ch = {}
    for c in cau_hois:
        did = c['ma_dia_diem']
        if did not in count_ch:
            count_ch[did] = 0
        count_ch[did] += 1
    print(f"\n  So dia diem: {len(dia_diems)}")
    print(f"  So manh moi: {len(manh_mois)}")
    print(f"  So cau hoi: {len(cau_hois)}")
    print(f"\n  KIEM TRA TUNG DIA DIEM:")
    day_du = 0
    for d in dia_diems:
        did = d['ma_dia_diem']
        ten = d['ten_dia_diem']
        stages = count_mm.get(did, [])
        n_ch = count_ch.get(did, 0)
        ok_mm = all(i in stages for i in [0,1,2,3])
        ok_ch = n_ch >= 3
        if ok_mm and ok_ch:
            day_du += 1
            print(f"    OK  [DD{did}] {ten} | 4 manh moi + {n_ch} cau hoi")
        else:
            miss_stages = set([0,1,2,3]) - set(stages)
            print(f"    BAD [DD{did}] {ten}")
            if not ok_mm:
                print(f"         MANH MOI: co stages={sorted(stages)}, THIEU stages={sorted(miss_stages)}")
            if not ok_ch:
                print(f"         CAU HOI: chi co {n_ch}/3 cau hoi")
    print(f"\n  KET LUAN: {day_du}/{len(dia_diems)} dia diem day du (4 manh moi + 3 cau hoi)")

if __name__ == '__main__':
    conn = get_conn()
    c = conn.cursor()
    dd = doc_dia_diem(c)
    doc_su_kien(c)
    mm = doc_manh_moi(c)
    ch = doc_cau_hoi(c)
    tong_ket(dd, mm, ch)
    conn.close()
    print("\nHOAN TAT!")

