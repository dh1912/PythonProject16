-- Phiên câu hỏi bền vững qua restart, không thay đổi ID/tiến độ cũ.
CREATE TABLE IF NOT EXISTS question_sessions (
 session_id TEXT PRIMARY KEY,
 ma_nguoi_dung INTEGER NOT NULL REFERENCES nguoi_dung(ma_nguoi_dung),
 ma_cau_hoi TEXT NOT NULL,
 started_at REAL NOT NULL,
 expires_at REAL NOT NULL,
 response_json TEXT,
 submitted_choice INTEGER
);
CREATE INDEX IF NOT EXISTS idx_sessions_player ON question_sessions(ma_nguoi_dung,ma_cau_hoi,expires_at);