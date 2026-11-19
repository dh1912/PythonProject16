-- Task 5: chỉ tạo bảng mới; không sửa các bảng game hiện có.
CREATE TABLE IF NOT EXISTS answer_log (
  answer_log_id BIGINT NOT NULL AUTO_INCREMENT,
  ma_nguoi_dung INT NOT NULL,
  ma_cau_hoi VARCHAR(100) NOT NULL,
  dung_sai TINYINT(1) NOT NULL,
  diem INT NOT NULL DEFAULT 0,
  thoi_gian DECIMAL(8,3) NOT NULL,
  PRIMARY KEY (answer_log_id),
  UNIQUE KEY uq_answer_user_question (ma_nguoi_dung, ma_cau_hoi),
  KEY idx_answer_question (ma_cau_hoi),
  CONSTRAINT fk_answer_log_user FOREIGN KEY (ma_nguoi_dung)
    REFERENCES nguoi_dung (ma_nguoi_dung) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS review_items (
  review_item_id BIGINT NOT NULL AUTO_INCREMENT,
  ma_nguoi_dung INT NOT NULL,
  ma_cau_hoi VARCHAR(100) NOT NULL,
  location_name VARCHAR(255) NOT NULL DEFAULT '',
  question_text TEXT NOT NULL,
  options_json LONGTEXT NOT NULL,
  correct_index INT NOT NULL,
  user_choice INT NOT NULL DEFAULT -1,
  explanation TEXT NOT NULL,
  source_title VARCHAR(512) NOT NULL DEFAULT '',
  source_citation TEXT NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
  retry_count INT NOT NULL DEFAULT 0,
  reward_awarded TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (review_item_id),
  UNIQUE KEY uq_review_user_question (ma_nguoi_dung, ma_cau_hoi),
  KEY idx_review_user_status (ma_nguoi_dung, status),
  CONSTRAINT fk_review_user FOREIGN KEY (ma_nguoi_dung)
    REFERENCES nguoi_dung (ma_nguoi_dung) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tai_khoan_bao_mat (
  ma_nguoi_dung INT NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (ma_nguoi_dung),
  CONSTRAINT fk_security_user FOREIGN KEY (ma_nguoi_dung)
    REFERENCES nguoi_dung (ma_nguoi_dung) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;