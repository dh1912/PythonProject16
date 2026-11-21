"""Khởi tạo SQLite an toàn: kết nối riêng/request, backup trước migration, không seed user."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sqlite3
import threading
from datetime import datetime, timezone

_lock = threading.RLock()


def database_path() -> Path:
    default_path=Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'HistoryGame' / 'game.db'
    return Path(os.environ.get('SQLITE_DB_PATH',str(default_path))).resolve()


def initialize(path: Path | None = None) -> Path:
    path = path or database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        existed = path.is_file() and path.stat().st_size > 0
        conn = sqlite3.connect(str(path), timeout=15)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute('PRAGMA busy_timeout=15000')
            conn.execute('PRAGMA foreign_keys=ON')
            version = conn.execute('PRAGMA user_version').fetchone()[0]
            if version < 5:
                if existed:
                    backup_path = path.with_name(path.name + '.backup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
                    with sqlite3.connect(str(backup_path)) as backup:
                        conn.backup(backup)
                schema = (Path(__file__).parent / 'migrations/005_task5_sqlite.sql').read_text(encoding='utf-8')
                # executescript mở transaction rõ ràng; backup không chứa dữ liệu thử.
                conn.executescript('BEGIN IMMEDIATE;\n' + schema)
                columns = {row[1] for row in conn.execute('PRAGMA table_info(tien_do_choi)')}
                if 'du_lieu_nhiem_vu' not in columns:
                    conn.execute("ALTER TABLE tien_do_choi ADD COLUMN du_lieu_nhiem_vu TEXT DEFAULT '{}'")
                conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS uq_progress_user ON tien_do_choi(ma_nguoi_dung)')
                # Database SQLite v4 có thể đã có bảng Task 5 tối giản. Chỉ bổ sung
                # cột còn thiếu; không DROP/REPLACE hàng người chơi.
                required_columns = {
                    'answer_log': {'answer_log_id':'INTEGER', 'ma_nguoi_dung':'INTEGER', 'ma_cau_hoi':"TEXT NOT NULL DEFAULT ''", 'dung_sai':'INTEGER NOT NULL DEFAULT 0', 'diem':'INTEGER NOT NULL DEFAULT 0', 'thoi_gian':'REAL NOT NULL DEFAULT 0'},
                    'review_items': {'review_item_id':'INTEGER', 'ma_nguoi_dung':'INTEGER', 'ma_cau_hoi':"TEXT NOT NULL DEFAULT ''", 'location_name':"TEXT NOT NULL DEFAULT ''", 'question_text':"TEXT NOT NULL DEFAULT ''", 'options_json':"TEXT NOT NULL DEFAULT '[]'", 'correct_index':'INTEGER NOT NULL DEFAULT 0', 'user_choice':'INTEGER NOT NULL DEFAULT -1', 'explanation':"TEXT NOT NULL DEFAULT ''", 'source_title':"TEXT NOT NULL DEFAULT ''", 'source_citation':"TEXT NOT NULL DEFAULT ''", 'status':"TEXT NOT NULL DEFAULT 'PENDING'", 'retry_count':'INTEGER NOT NULL DEFAULT 0', 'reward_awarded':'INTEGER NOT NULL DEFAULT 0'},
                    'tai_khoan_bao_mat': {'ma_nguoi_dung':'INTEGER', 'password_hash':"TEXT NOT NULL DEFAULT ''"},
                }
                for table, definitions in required_columns.items():
                    existing = {row[1] for row in conn.execute(f'PRAGMA table_info({table})')}
                    for column, definition in definitions.items():
                        if column not in existing:
                            conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')
                seed = Path(__file__).parent / 'historical_seed.json'
                if seed.is_file():
                    for table, rows in json.loads(seed.read_text(encoding='utf-8')).items():
                        if table not in {'dia_diem','su_kien_lich_su','nhan_vat','manh_moi','cau_hoi_on_tap'}:
                            raise ValueError('Bảng seed không được phép')
                        for row in rows:
                            names = list(row)
                            conn.execute(f"INSERT INTO {table} ({','.join(names)}) VALUES ({','.join('?' for _ in names)}) ON CONFLICT DO NOTHING", tuple(row.values()))
                # Chuyển chính xác legacy bcrypt hợp lệ; plaintext cần reset, không login tự động.
                for uid, hashed in conn.execute('SELECT ma_nguoi_dung,mat_khau_ma_hoa FROM nguoi_dung'):
                    if isinstance(hashed,str) and hashed.startswith(('$2a$','$2b$','$2y$')):
                        conn.execute('INSERT INTO tai_khoan_bao_mat(ma_nguoi_dung,password_hash) VALUES(?,?) ON CONFLICT DO NOTHING',(uid,hashed))
                conn.execute('PRAGMA user_version=5')
                conn.commit()
            if os.getenv('SQLITE_WAL', '1') == '1':
                conn.execute('PRAGMA journal_mode=WAL')
            if version < 6:
                if existed:
                    backup_path=path.with_name(path.name+'.backup-v6-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
                    with sqlite3.connect(str(backup_path)) as backup:
                        conn.backup(backup)
                conn.executescript('BEGIN IMMEDIATE;\n'+(Path(__file__).parent/'migrations/006_history_content.sql').read_text(encoding='utf-8'))
                from data.content_v6 import migrate
                migrate(conn)
                conn.execute('PRAGMA user_version=6')
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    return path


def connect() -> sqlite3.Connection:
    path = initialize()
    conn = sqlite3.connect(str(path), timeout=15)
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=15000')
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    return conn


def backup_database(destination: Path) -> Path:
    """Backup nhất quán kể cả khi WAL đang bật; đích phải khác DB nguồn."""
    source = database_path()
    destination = destination.resolve()
    if destination == source or destination in source.parents:
        raise ValueError('Đường dẫn backup không an toàn.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(str(source), timeout=15)
    try:
        dst = sqlite3.connect(str(destination))
        try:
            src.backup(dst)
            check = dst.execute('PRAGMA integrity_check').fetchone()[0]
            if check != 'ok':
                raise sqlite3.DatabaseError('Backup integrity_check thất bại: '+str(check))
        finally:
            dst.close()
    finally:
        src.close()
    return destination