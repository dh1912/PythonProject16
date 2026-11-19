-- ========================================================
-- TASK 4: MIGRATION CƠ SỞ DỮ LIỆU HOÀN THIỆN
-- Bổ sung đầy đủ 4 mốc lịch sử, 16 manh mối nhân - quả (0..3)
-- và 12 câu hỏi trắc nghiệm kiểm chứng cho Task 4
-- ========================================================

USE `game`;

-- 1. Bổ sung cột lưu tiến độ FSM Task 4 vào bảng tien_do_choi
ALTER TABLE `tien_do_choi` 
ADD COLUMN IF NOT EXISTS `du_lieu_nhiem_vu` LONGTEXT DEFAULT NULL;

-- 2. Đảm bảo đầy đủ địa danh Dinh Độc Lập (mã 9) và sự kiện 30
INSERT INTO `dia_diem` (`ma_dia_diem`, `ten_dia_diem`, `toa_do_x`, `toa_do_y`, `khu_vuc`, `mo_ta`, `mo_khoa_mac_dinh`)
VALUES (9, 'Dinh Độc Lập (Sài Gòn)', 380, 505, 'Nam', 'Nơi giải phóng hoàn toàn miền Nam ngày 30/4/1975.', 0)
ON DUPLICATE KEY UPDATE `ten_dia_diem` = VALUES(`ten_dia_diem`);

INSERT INTO `su_kien_lich_su` (`ma_su_kien`, `ma_dia_diem`, `ten_su_kien`, `nam_dien_ra`, `ngay_thang_chi_tiet`, `thoi_ky`, `tom_tat_dien_bien`, `nguon_trich_dan`)
VALUES (30, 9, 'Đại thắng mùa Xuân 1975 - Giải phóng miền Nam', 1975, '30/04/1975', '1954 - 1975', '11h30 trưa 30/4/1975, xe tăng quân giải phóng tiến vào Dinh Độc Lập, cắm cờ chiến thắng.', 'Đại thắng mùa Xuân 1975, NXB Quân đội Nhân dân')
ON DUPLICATE KEY UPDATE `ten_su_kien` = VALUES(`ten_su_kien`);

-- 3. Nạp đầy đủ 4 giai đoạn nhân - quả (thu_tu_timeline_dung: 0..3) cho 4 mốc lớn
DELETE FROM `manh_moi` WHERE `ma_su_kien` IN (20, 25, 29, 30);

INSERT INTO `manh_moi` (`ma_su_kien`, `ma_nhan_vat`, `tieu_de_manh_moi`, `loai_manh_moi`, `noi_dung_chi_tiet`, `thu_tu_timeline_dung`) VALUES
(20, 4, 'Nguyễn Ái Quốc trở về Tổ quốc', 'hiện vật', 'Ngày 28/01/1941, Người qua mốc 108 Cao Bằng về nước.', 0),
(20, 4, 'Hội nghị Trung ương lần thứ tám', 'văn kiện', 'Họp từ 10 đến 19/5/1941 tại Pác Bó đặt giải phóng dân tộc lên hàng đầu.', 1),
(20, 4, 'Thành lập Mặt trận Việt Minh', 'văn kiện', 'Quyết định thành lập Việt Nam Độc lập Đồng minh ngày 19/5/1941.', 2),
(20, 4, 'Chuẩn bị lực lượng giải phóng dân tộc', 'lời khai', 'Cao Bằng trở thành căn cứ địa cách mạng đầu tiên của cả nước.', 3),
(25, 6, 'Tổng khởi nghĩa giành chính quyền', 'lời khai', 'Tháng Tám năm 1945, nhân dân cả nước nổi dậy giành chính quyền thắng lợi.', 0),
(25, 6, 'Chính phủ lâm thời ra đời', 'văn kiện', 'Ủy ban Dân tộc Giải phóng cải tổ thành Chính phủ lâm thời nước VNDCCH.', 1),
(25, 6, 'Tuyên ngôn Độc lập được soạn thảo', 'văn kiện', 'Bác Hồ soạn thảo bản Tuyên ngôn tại căn nhà số 48 Hàng Ngang, Hà Nội.', 2),
(25, 6, 'Tuyên bố độc lập tại Ba Đình', 'hiện vật', 'Ngày 2/9/1945, Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa.', 3),
(29, 8, 'Chiến dịch Đông Xuân 1953-1954', 'lời khai', 'Quân và dân ta chủ động tấn công phân tán lực lượng cơ động của Pháp.', 0),
(29, 8, 'Điện Biên Phủ thành tập đoàn cứ điểm', 'hiện vật', 'Pháp xây dựng Điện Biên Phủ thành pháo đài bất khả xâm phạm.', 1),
(29, 8, 'Mở màn chiến dịch', 'lời khai', 'Trận mở màn Him Lam chiều ngày 13/3/1954 giáng đòn sấm sét vào quân Pháp.', 2),
(29, 8, 'Chiến thắng ngày 7/5/1954', 'hiện vật', '17h30 chiều 7/5/1954, tướng De Castries đầu hàng, tập đoàn cứ điểm bị xóa sổ.', 3),
(30, 8, 'Hiệp định Paris được ký kết', 'văn kiện', 'Ngày 27/1/1973, Hiệp định Paris buộc đế quốc Mỹ phải rút hết quân về nước.', 0),
(30, 8, 'Giải phóng Tây Nguyên và miền Trung', 'lời khai', 'Cuộc Tổng tiến công mùa Xuân 1975 giải phóng Buôn Ma Thuột, Huế, Đà Nẵng.', 1),
(30, 8, 'Chiến dịch Hồ Chí Minh bắt đầu', 'văn kiện', 'Chiến dịch lịch sử giải phóng Sài Gòn mở màn ngày 26/4/1975.', 2),
(30, 8, 'Dinh Độc Lập được giải phóng', 'hiện vật', 'Trưa 30/4/1975, xe tăng húc đổ cổng Dinh Độc Lập, non sông thu về một mối.', 3);


-- 4. Bổ sung đủ bộ 3 câu hỏi trắc nghiệm kiểm chứng cho 4 mốc lớn
DELETE FROM `cau_hoi_on_tap` WHERE `ma_su_kien` IN (20, 25, 29, 30);

INSERT INTO `cau_hoi_on_tap` (`ma_su_kien`, `noi_dung_cau_hoi`, `dap_an_a`, `dap_an_b`, `dap_an_c`, `dap_an_d`, `dap_an_dung`, `giai_thich_chi_tiet`) VALUES
(20, 'Nguyễn Ái Quốc trở về Tổ quốc vào năm nào?', '1930', '1941', '1945', '1954', 'B', 'Người trở về nước ngày 28/01/1941 qua mốc biên giới 108.'),
(20, 'Hội nghị Trung ương 8 họp vào tháng nào?', '1/1941', '3/1941', '5/1941', '8/1941', 'C', 'Hội nghị diễn ra từ ngày 10 đến 19/5/1941 tại Pác Bó.'),
(20, 'Mặt trận được thành lập tại Hội nghị Trung ương 8 có tên gì?', 'Việt Minh', 'Mặt trận Liên Việt', 'Mặt trận Dân chủ', 'Mặt trận Tổ quốc', 'A', 'Việt Nam Độc lập Đồng minh (Việt Minh) ra đời năm 1941.'),
(25, 'Tuyên ngôn Độc lập được đọc vào ngày nào?', '19/08/1945', '02/09/1945', '07/05/1954', '19/12/1946', 'B', 'Tuyên ngôn được đọc tại Ba Đình ngày 2/9/1945.'),
(25, 'Ai là người thay mặt Chính phủ lâm thời đọc Tuyên ngôn Độc lập?', 'Trường Chinh', 'Võ Nguyên Giáp', 'Hồ Chí Minh', 'Phạm Văn Đồng', 'C', 'Chủ tịch Hồ Chí Minh thay mặt Chính phủ lâm thời đọc Tuyên ngôn.'),
(25, 'Tên nước được khai sinh ngày 2/9/1945 là gì?', 'Việt Nam Dân chủ Cộng hòa', 'Cộng hòa XHCN Việt Nam', 'Đại Nam', 'Việt Nam Cộng hòa', 'A', 'Nước Việt Nam Dân chủ Cộng hòa ra đời ngày 2/9/1945.'),
(29, 'Chiến dịch Điện Biên Phủ toàn thắng vào ngày nào?', '07/05/1954', '20/07/1954', '02/09/1954', '19/12/1954', 'A', 'Chiến dịch toàn thắng ngày 7/5/1954.'),
(29, 'Chiến dịch Điện Biên Phủ bắt đầu vào ngày nào?', '13/03/1954', '07/05/1954', '19/12/1946', '01/09/1954', 'A', 'Chiến dịch mở màn ngày 13/3/1954.'),
(29, 'Ai là Tổng Tư lệnh chiến dịch Điện Biên Phủ?', 'Võ Nguyên Giáp', 'Văn Tiến Dũng', 'Nguyễn Chí Thanh', 'Hoàng Văn Thái', 'A', 'Đại tướng Võ Nguyên Giáp là Tổng Tư lệnh chiến dịch.'),
(30, 'Chiến dịch Hồ Chí Minh toàn thắng ngày nào?', '30/04/1975', '01/05/1975', '26/04/1975', '02/09/1975', 'A', 'Chiến dịch kết thúc thắng lợi ngày 30/4/1975.'),
(30, 'Chiến dịch Hồ Chí Minh mở màn ngày nào?', '26/04/1975', '30/04/1975', '07/05/1954', '27/01/1973', 'A', 'Chiến dịch bắt đầu ngày 26/4/1975.'),
(30, 'Xe tăng nào đã húc đổ cổng chính Dinh Độc Lập?', 'Xe tăng 390', 'Xe tăng 843', 'Xe tăng 985', 'Xe tăng 280', 'A', 'Xe tăng 390 húc đổ cổng chính Dinh Độc Lập.');
