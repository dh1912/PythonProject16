-- Không xóa dữ liệu legacy: manifest chỉ định bộ nội dung chính thức mới.
CREATE TABLE IF NOT EXISTS moc_lich_su(ma_moc INTEGER PRIMARY KEY,nam INTEGER,ngay_thang TEXT,thoi_ky TEXT,y_nghia_giai_doan TEXT);
CREATE TABLE IF NOT EXISTS nguon_lich_su(ma_nguon INTEGER PRIMARY KEY,ten_tai_lieu TEXT,loai_nguon TEXT,tac_gia_co_quan TEXT,nha_xuat_ban TEXT,nam_xuat_ban INTEGER,trich_dan_chi_tiet TEXT,muc_do_xac_thuc TEXT);
CREATE TABLE IF NOT EXISTS nhan_vat_lich_su(ma_nhan_vat INTEGER PRIMARY KEY,ten_nhan_vat TEXT,nam_sinh_mat TEXT,vai_tro TEXT,tieu_su_dong_gop TEXT);
CREATE TABLE IF NOT EXISTS su_kien_nhan_vat(ma_su_kien INTEGER REFERENCES su_kien_lich_su,ma_nhan_vat INTEGER REFERENCES nhan_vat_lich_su,vai_tro_trong_su_kien TEXT,PRIMARY KEY(ma_su_kien,ma_nhan_vat));
CREATE TABLE IF NOT EXISTS tui_do_nguoi_choi(ma_tui_do INTEGER PRIMARY KEY,ma_nguoi_dung INTEGER REFERENCES nguoi_dung,ma_manh_moi INTEGER REFERENCES manh_moi,thoi_gian_thu_thap TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(ma_nguoi_dung,ma_manh_moi));
CREATE TABLE IF NOT EXISTS content_manifest(source_key TEXT PRIMARY KEY,table_name TEXT NOT NULL,row_id INTEGER NOT NULL);
-- Mở rộng bảng SQLite Task 5 cũ theo kiểu additive, không xóa/replace dữ liệu.
CREATE TABLE IF NOT EXISTS answer_log (
 answer_log_id INTEGER PRIMARY KEY,ma_nguoi_dung INTEGER NOT NULL REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_cau_hoi TEXT NOT NULL,dung_sai INTEGER NOT NULL,diem INTEGER NOT NULL,thoi_gian REAL NOT NULL,
 UNIQUE(ma_nguoi_dung,ma_cau_hoi));
CREATE TABLE IF NOT EXISTS review_items (
 review_item_id INTEGER PRIMARY KEY,ma_nguoi_dung INTEGER NOT NULL REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_cau_hoi TEXT NOT NULL,location_name TEXT DEFAULT '',question_text TEXT NOT NULL,options_json TEXT NOT NULL,
 correct_index INTEGER NOT NULL,user_choice INTEGER DEFAULT -1,explanation TEXT DEFAULT '',source_title TEXT DEFAULT '',
 source_citation TEXT DEFAULT '',status TEXT NOT NULL DEFAULT 'PENDING',retry_count INTEGER DEFAULT 0,
 reward_awarded INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(ma_nguoi_dung,ma_cau_hoi));
CREATE TABLE IF NOT EXISTS tai_khoan_bao_mat (
 ma_nguoi_dung INTEGER PRIMARY KEY REFERENCES nguoi_dung(ma_nguoi_dung),password_hash TEXT NOT NULL,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP);