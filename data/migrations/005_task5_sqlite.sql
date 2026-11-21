-- SQLite, phiên bản 5: không DROP bảng hoặc thay thế dữ liệu người chơi.
CREATE TABLE IF NOT EXISTS nguoi_dung (
 ma_nguoi_dung INTEGER PRIMARY KEY, ten_dang_nhap TEXT NOT NULL UNIQUE,
 mat_khau_ma_hoa TEXT NOT NULL, ho_va_ten TEXT NOT NULL, vai_tro TEXT NOT NULL DEFAULT 'player',
 ngay_tao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS tien_do_choi (
 ma_tien_do INTEGER PRIMARY KEY, ma_nguoi_dung INTEGER NOT NULL UNIQUE REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_dia_diem_hien_tai INTEGER DEFAULT 1, nam_mo_khoa_cao_nhat INTEGER DEFAULT 1914,
 diem_tri_thuc INTEGER NOT NULL DEFAULT 0, danh_sach_dia_diem_da_mo TEXT DEFAULT '[]',
 du_lieu_nhiem_vu TEXT DEFAULT '{}', thoi_gian_cap_nhat TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS dia_diem (
 ma_dia_diem INTEGER PRIMARY KEY, ten_dia_diem TEXT NOT NULL, toa_do_x REAL, toa_do_y REAL,
 khu_vuc TEXT, mo_ta TEXT, mo_khoa_mac_dinh INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS su_kien_lich_su (
 ma_su_kien INTEGER PRIMARY KEY, ma_dia_diem INTEGER REFERENCES dia_diem(ma_dia_diem),
 ten_su_kien TEXT NOT NULL, nam_dien_ra INTEGER, ngay_thang_chi_tiet TEXT, thoi_ky TEXT,
 tom_tat_dien_bien TEXT, nguon_trich_dan TEXT);
CREATE TABLE IF NOT EXISTS nhan_vat (
 ma_nhan_vat INTEGER PRIMARY KEY, ma_dia_diem INTEGER REFERENCES dia_diem(ma_dia_diem),
 ten_nhan_vat TEXT, loai_nhan_vat TEXT, loi_thoai TEXT);
CREATE TABLE IF NOT EXISTS manh_moi (
 ma_manh_moi INTEGER PRIMARY KEY, ma_su_kien INTEGER REFERENCES su_kien_lich_su(ma_su_kien),
 ma_nhan_vat INTEGER REFERENCES nhan_vat(ma_nhan_vat), tieu_de_manh_moi TEXT, loai_manh_moi TEXT,
 noi_dung_chi_tiet TEXT, thu_tu_timeline_dung INTEGER);
CREATE TABLE IF NOT EXISTS cau_hoi_on_tap (
 ma_cau_hoi INTEGER PRIMARY KEY, ma_su_kien INTEGER REFERENCES su_kien_lich_su(ma_su_kien),
 noi_dung_cau_hoi TEXT, dap_an_a TEXT, dap_an_b TEXT, dap_an_c TEXT, dap_an_d TEXT,
 dap_an_dung TEXT, giai_thich_chi_tiet TEXT);
CREATE TABLE IF NOT EXISTS answer_log (
 answer_log_id INTEGER PRIMARY KEY, ma_nguoi_dung INTEGER NOT NULL REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_cau_hoi TEXT NOT NULL, dung_sai INTEGER NOT NULL, diem INTEGER NOT NULL,
 thoi_gian REAL NOT NULL, UNIQUE(ma_nguoi_dung,ma_cau_hoi));
CREATE TABLE IF NOT EXISTS review_items (
 review_item_id INTEGER PRIMARY KEY, ma_nguoi_dung INTEGER NOT NULL REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_cau_hoi TEXT NOT NULL, location_name TEXT DEFAULT '', question_text TEXT NOT NULL,
 options_json TEXT NOT NULL, correct_index INTEGER NOT NULL, user_choice INTEGER DEFAULT -1,
 explanation TEXT DEFAULT '', source_title TEXT DEFAULT '', source_citation TEXT DEFAULT '',
 status TEXT NOT NULL DEFAULT 'PENDING', retry_count INTEGER DEFAULT 0, reward_awarded INTEGER DEFAULT 0,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(ma_nguoi_dung,ma_cau_hoi));
CREATE TABLE IF NOT EXISTS tai_khoan_bao_mat (
 ma_nguoi_dung INTEGER PRIMARY KEY REFERENCES nguoi_dung(ma_nguoi_dung), password_hash TEXT NOT NULL,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_review_status ON review_items(ma_nguoi_dung,status);