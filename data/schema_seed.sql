-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th10 11, 2026 lúc 05:05 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `game`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `cau_hoi_on_tap`
--

CREATE TABLE `cau_hoi_on_tap` (
  `ma_cau_hoi` int(11) NOT NULL,
  `ma_su_kien` int(11) DEFAULT NULL,
  `noi_dung_cau_hoi` text NOT NULL,
  `dap_an_a` varchar(255) NOT NULL,
  `dap_an_b` varchar(255) NOT NULL,
  `dap_an_c` varchar(255) NOT NULL,
  `dap_an_d` varchar(255) NOT NULL,
  `dap_an_dung` char(1) NOT NULL,
  `giai_thich_chi_tiet` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `cau_hoi_on_tap`
--

INSERT INTO `cau_hoi_on_tap` (`ma_cau_hoi`, `ma_su_kien`, `noi_dung_cau_hoi`, `dap_an_a`, `dap_an_b`, `dap_an_c`, `dap_an_d`, `dap_an_dung`, `giai_thich_chi_tiet`) VALUES
(1, 9, 'Nguyễn Tất Thành ra đi tìm đường cứu nước từ bến cảng nào vào năm 1911?', 'Cảng Đà Nẵng', 'Bến Nhà Rồng (Sài Gòn)', 'Cảng Hải Phòng', 'Cảng Cửa Lò', 'B', 'Ngày 5/6/1911, người thanh niên yêu nước Nguyễn Tất Thành lấy tên Văn Ba rời bến cảng Nhà Rồng ra đi cứu nước.'),
(2, 14, 'Đảng Cộng sản Việt Nam được thành lập vào ngày tháng năm nào?', '03/02/1930', '02/09/1945', '19/08/1945', '28/01/1941', 'A', 'Ngày 3/2/1930 tại Hương Cảng, Hội nghị hợp nhất các tổ chức cộng sản do Nguyễn Ái Quốc chủ trì đã quyết định thành lập Đảng.'),
(3, 16, 'Phong trào đấu tranh cách mạng tiêu biểu nhất trong giai đoạn 1930 - 1931 là gì?', 'Khởi nghĩa Yên Bái', 'Khởi nghĩa Ba Tơ', 'Xô viết Nghệ - Tĩnh', 'Khởi nghĩa Nam Kỳ', 'C', 'Phong trào Xô viết Nghệ - Tĩnh là đỉnh cao của cao trào cách mạng 1930-1931, lập ra chính quyền của công nông.'),
(4, 20, 'Nguyễn Ái Quốc trở về Tổ quốc trực tiếp lãnh đạo cách mạng vào thời gian nào?', 'Mùa thu năm 1940', 'Đầu năm 1941', 'Tháng 8 năm 1945', 'Cuối năm 1946', 'B', 'Ngày 28/01/1941, Bác qua mốc 108 biên giới Việt - Trung về đến hang Pác Bó (Cao Bằng).'),
(5, 23, 'Đại hội Quốc dân Tân Trào (16/8/1945) đã đưa ra quyết định quan trọng nào?', 'Ký hiệp định đình chiến', 'Tán thành lệnh Tổng khởi nghĩa giành chính quyền', 'Kháng chiến toàn quốc', 'Đổi tên Đảng', 'B', 'Quốc dân Đại hội Tân Trào đã thông qua lệnh Tổng khởi nghĩa giành chính quyền trước khi quân Đồng minh vào Đông Dương.'),
(6, 25, 'Bản Tuyên ngôn Độc lập được Chủ tịch Hồ Chí Minh đọc tại đâu vào ngày 2/9/1945?', 'Nhà hát Lớn Hà Nội', 'Quảng trường Ba Đình', 'Bắc Bộ Phủ', 'Đình Tân Trào', 'B', 'Ngày 2/9/1945 tại Quảng trường Ba Đình, Bác Hồ đã đọc bản Tuyên ngôn Độc lập khai sinh nước VNDCCH.'),
(7, 27, 'Chiến dịch nào đã bảo vệ an toàn cơ quan đầu não kháng chiến trong Thu - Đông 1947?', 'Chiến dịch Điện Biên Phủ', 'Chiến dịch Tây Bắc', 'Chiến dịch Việt Bắc Thu - Đông 1947', 'Chiến dịch Biên Giới 1950', 'C', 'Chiến thắng Việt Bắc Thu - Đông 1947 đã phá tan chiến lược đánh nhanh thắng nhanh của giặc Pháp.'),
(8, 29, 'Chiến dịch Điện Biên Phủ kết thúc thắng lợi hoàn toàn vào ngày nào?', '07/05/1954', '20/07/1954', '02/09/1954', '19/12/1954', 'A', 'Vào lúc 17h30 ngày 07/05/1954, cứ điểm Điện Biên Phủ bị tiêu diệt hoàn toàn, tướng De Castries bị bắt sống.');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `dia_diem`
--

CREATE TABLE `dia_diem` (
  `ma_dia_diem` int(11) NOT NULL,
  `ten_dia_diem` varchar(100) NOT NULL,
  `toa_do_x` float NOT NULL,
  `toa_do_y` float NOT NULL,
  `khu_vuc` varchar(50) NOT NULL,
  `mo_ta` text DEFAULT NULL,
  `mo_khoa_mac_dinh` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `dia_diem`
--

INSERT INTO `dia_diem` (`ma_dia_diem`, `ten_dia_diem`, `toa_do_x`, `toa_do_y`, `khu_vuc`, `mo_ta`, `mo_khoa_mac_dinh`) VALUES
(1, 'Bến Nhà Rồng (Sài Gòn)', 412, 490, 'Nam', 'Nơi người thanh niên yêu nước Nguyễn Tất Thành ra đi tìm đường cứu nước năm 1911.', 1),
(2, 'Hương Cảng (Hong Kong)', 525, 203, 'Ngoại cảnh', 'Nơi Nguyễn Ái Quốc chủ trì Hội nghị thành lập Đảng Cộng sản Việt Nam năm 1930.', 0),
(3, 'Vinh - Bến Thủy (Nghệ An)', 376, 286, 'Trung', 'Đỉnh cao phong trào cách mạng 1930-1931 với chính quyền Xô viết Nghệ - Tĩnh.', 0),
(4, 'Hang Pác Bó (Cao Bằng)', 391, 183, 'Bắc', 'Căn cứ địa đầu tiên khi Bác Hồ về nước đầu năm 1941 lãnh đạo cách mạng.', 0),
(5, 'Tân Trào (Tuyên Quang)', 367, 201, 'Bắc', 'Thủ đô Khu giải phóng, nơi diễn ra Quốc dân Đại hội phát lệnh Tổng khởi nghĩa 1945.', 0),
(6, 'Quảng trường Ba Đình (Hà Nội)', 387, 224, 'Bắc', 'Nơi Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập ngày 2/9/1945.', 0),
(7, 'Căn cứ địa Việt Bắc', 389, 207, 'Bắc', 'Thủ đô kháng chiến chống thực dân Pháp, chiến thắng Việt Bắc 1947 & Biên giới 1950.', 0),
(8, 'Lòng chảo Điện Biên Phủ', 299, 217, 'Bắc', 'Tập đoàn cứ điểm mạnh nhất Đông Dương của Pháp, chiến thắng chấn động địa cầu năm 1954.', 0);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `manh_moi`
--

CREATE TABLE `manh_moi` (
  `ma_manh_moi` int(11) NOT NULL,
  `ma_su_kien` int(11) DEFAULT NULL,
  `ma_nhan_vat` int(11) DEFAULT NULL,
  `tieu_de_manh_moi` varchar(150) NOT NULL,
  `loai_manh_moi` varchar(30) NOT NULL,
  `noi_dung_chi_tiet` text NOT NULL,
  `thu_tu_timeline_dung` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `manh_moi`
--

INSERT INTO `manh_moi` (`ma_manh_moi`, `ma_su_kien`, `ma_nhan_vat`, `tieu_de_manh_moi`, `loai_manh_moi`, `noi_dung_chi_tiet`, `thu_tu_timeline_dung`) VALUES
(1, 9, 1, 'Thẻ thủy thủ tàu Latouche-Tréville', 'hiện vật', 'Tên đăng ký Văn Ba, lên tàu ngày 5/6/1911 bắt đầu hành trình sang phương Tây.', 1),
(2, 9, NULL, 'Lòng yêu nước thương dân sâu sắc', 'văn kiện', 'Động lực quyết định thôi thúc người thanh niên yêu nước ra đi tìm con đường cứu nước mới.', 2),
(3, 14, 2, 'Chánh cương vắn tắt của Đảng', 'văn kiện', 'Văn kiện thông qua tại Hội nghị 3/2/1930 vạch ra đường lối giải phóng dân tộc đúng đắn.', 1),
(4, 16, 3, 'Trống lệnh biểu tình Xô Viết', 'hiện vật', 'Tiếng trống mở đầu cho cuộc bãi công, biểu tình vũ trang của nhân dân Nghệ - Tĩnh.', 1),
(5, 20, 4, 'Cột mốc biên giới 108', 'hiện vật', 'Cột mốc lịch sử nơi Bác Hồ đặt bước chân đầu tiên trở về đất mẹ ngày 28/01/1941.', 1),
(6, 20, NULL, 'Nghị quyết Trung ương 8 (5/1941)', 'văn kiện', 'Quyết định đặt nhiệm vụ giải phóng dân tộc lên hàng đầu và thành lập Mặt trận Việt Minh.', 2),
(7, 23, 5, 'Quân lệnh số 1', 'văn kiện', 'Ủy ban Khởi nghĩa toàn quốc ban bố lệnh phát động Tổng khởi nghĩa đêm 13/8/1945.', 1),
(8, 25, 6, 'Bản thảo Tuyên ngôn Độc lập', 'văn kiện', 'Soạn thảo tại 48 Hàng Ngang, khẳng định quyền độc lập, tự do thiêng liêng của dân tộc.', 1),
(9, 27, 7, 'Chỉ thị Phá tan cuộc tấn công mùa đông của giặc Pháp', 'văn kiện', 'Ban Thường vụ Trung ương Đảng chỉ đạo chiến đấu bảo vệ căn cứ địa Việt Bắc.', 1),
(10, 29, 8, 'Lá cờ Quyết chiến Quyết thắng', 'hiện vật', 'Phất cao trên nóc hầm tướng De Castries lúc 17h30 chiều ngày 07/05/1954.', 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `moc_lich_su`
--

CREATE TABLE `moc_lich_su` (
  `ma_moc` int(11) NOT NULL,
  `nam` int(11) NOT NULL,
  `ngay_thang` varchar(50) DEFAULT NULL,
  `thoi_ky` varchar(100) NOT NULL,
  `y_nghia_giai_doan` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `moc_lich_su`
--

INSERT INTO `moc_lich_su` (`ma_moc`, `nam`, `ngay_thang`, `thoi_ky`, `y_nghia_giai_doan`) VALUES
(1, 1858, '01/09/1858', '1858 - 1918', 'Giai đoạn kháng chiến chống thực dân Pháp xâm lược nửa cuối thế kỷ XIX.'),
(2, 1862, '05/06/1862', '1858 - 1918', 'Giai đoạn thực dân Pháp từng bước chiếm đóng các tỉnh Nam Kỳ.'),
(3, 1864, '20/08/1864', '1858 - 1918', 'Phong trào vũ trang chống Pháp của nghĩa sĩ Nam Kỳ.'),
(4, 1884, '06/06/1884', '1858 - 1918', 'Thời kỳ thiết lập ách đô hộ của chủ nghĩa thực dân Pháp.'),
(5, 1885, '13/07/1885', '1858 - 1918', 'Phong trào Cần Vương yêu nước (1885-1896).'),
(6, 1887, 'Giai đoạn 1884 - 1913', '1858 - 1918', 'Phong trào đấu tranh tự vệ của nông dân chống khai thác thuộc địa.'),
(7, 1904, 'Tháng 05/1904', '1858 - 1918', 'Phong trào yêu nước theo khuynh hướng dân chủ tư sản đầu thế kỷ XX.'),
(8, 1907, 'Tháng 03/1907', '1858 - 1918', 'Cao trào duy tân văn hóa xã hội đầu thế kỷ XX.'),
(9, 1911, '05/06/1911', '1858 - 1930', 'Thời kỳ Nguyễn Ái Quốc bôn ba khảo sát thực tiễn phong trào thế giới.'),
(10, 1919, '18/06/1919', '1919 - 1930', 'Phong trào yêu nước và cách mạng Việt Nam sau Chiến tranh thế giới thứ nhất.'),
(11, 1920, 'Tháng 12/1920', '1919 - 1930', 'Thời kỳ xác lập con đường cách mạng vô sản cho Việt Nam.'),
(12, 1925, 'Tháng 06/1925', '1919 - 1930', 'Thời kỳ chuẩn bị về tư tưởng, chính trị và tổ chức cho việc thành lập Đảng.'),
(13, 1927, 'Năm 1927', '1919 - 1930', 'Thời kỳ hoàn thiện đường lối chiến lược cách mạng giải phóng dân tộc.'),
(14, 1930, '03/02/1930', '1930 - 1945', 'Thời kỳ đấu tranh giành chính quyền dưới sự lãnh đạo của Đảng (1930-1945).'),
(15, 1930, '09/02/1930', '1930 - 1945', 'Phong trào đấu tranh sôi nổi đầu năm 1930.'),
(16, 1930, '12/09/1930', '1930 - 1945', 'Cao trào cách mạng 1930 - 1931.'),
(17, 1930, 'Tháng 10/1930', '1930 - 1945', 'Thời kỳ hoàn thiện hệ thống lãnh đạo của Đảng.'),
(18, 1936, 'Giai đoạn 1936 - 1939', '1930 - 1945', 'Thời kỳ vận động dân chủ rộng lớn.'),
(19, 1940, 'Cuối năm 1940', '1930 - 1945', 'Thời kỳ mở đầu giai đoạn khởi nghĩa vũ trang.'),
(20, 1941, '28/01/1941', '1930 - 1945', 'Thời kỳ chuẩn bị trực tiếp Tổng khởi nghĩa giành chính quyền.'),
(21, 1941, '19/05/1941', '1930 - 1945', 'Thời kỳ cao trào giải phóng dân tộc dưới ngọn cờ Việt Minh.'),
(22, 1944, '22/12/1944', '1930 - 1945', 'Thời kỳ xây dựng lực lượng vũ trang nòng cốt chuẩn bị khởi nghĩa.'),
(23, 1945, '16/08/1945', '1930 - 1945', 'Thời kỳ đỉnh cao Tổng khởi nghĩa Tháng Tám 1945.'),
(24, 1945, '19/08/1945', '1930 - 1945', 'Tuần lễ tổng khởi nghĩa tháng Tám hào hùng.'),
(25, 1945, '02/09/1945', '1930 - 1945', 'Khai sinh nước Việt Nam Dân chủ Cộng hòa.'),
(26, 1946, '19/12/1946', '1945 - 1954', 'Thời kỳ kháng chiến chống thực dân Pháp xâm lược (1945-1954).'),
(27, 1947, 'Thu - Đông 1947', '1945 - 1954', 'Giai đoạn chuyển từ cầm cự sang phản công trong kháng chiến chống Pháp.'),
(28, 1950, 'Thu - Đông 1950', '1945 - 1954', 'Thời kỳ giành quyền chủ động chiến lược trên chiến trường.'),
(29, 1954, '07/05/1954', '1945 - 1954', 'Đỉnh cao chiến thắng kháng chiến chống Pháp kết thúc bằng Hiệp định Giơ-ne-vơ.'),
(30, 1975, '30/04/1975', '1954 - 1975', 'Thời kỳ kháng chiến chống Mỹ, cứu nước kết thúc toàn thắng (1954-1975).');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nguoi_dung`
--

CREATE TABLE `nguoi_dung` (
  `ma_nguoi_dung` int(11) NOT NULL,
  `ten_dang_nhap` varchar(50) NOT NULL,
  `mat_khau_ma_hoa` varchar(255) NOT NULL,
  `ho_va_ten` varchar(100) NOT NULL,
  `vai_tro` varchar(20) DEFAULT 'player',
  `ngay_tao` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nguoi_dung`
--


-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nguon_lich_su`
--

CREATE TABLE `nguon_lich_su` (
  `ma_nguon` int(11) NOT NULL,
  `ten_tai_lieu` varchar(255) NOT NULL,
  `loai_nguon` varchar(50) DEFAULT 'Sách',
  `tac_gia_co_quan` varchar(255) DEFAULT NULL,
  `nha_xuat_ban` varchar(150) DEFAULT NULL,
  `nam_xuat_ban` int(11) DEFAULT NULL,
  `trich_dan_chi_tiet` text DEFAULT NULL,
  `muc_do_xac_thuc` varchar(50) DEFAULT 'Chính thống - Cấp Quốc gia'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nguon_lich_su`
--

INSERT INTO `nguon_lich_su` (`ma_nguon`, `ten_tai_lieu`, `loai_nguon`, `tac_gia_co_quan`, `nha_xuat_ban`, `nam_xuat_ban`, `trich_dan_chi_tiet`, `muc_do_xac_thuc`) VALUES
(1, 'Đại cương Lịch sử Việt Nam, Tập 2', 'Giáo trình chuẩn đại học', 'GS. Đinh Xuân Lâm (Chủ biên)', 'Giáo dục Việt Nam', 2006, 'Chương I: Cuộc kháng chiến chống thực dân Pháp xâm lược (1858-1884), tr. 15-22.', 'Chính thống - Cấp Quốc gia'),
(2, 'Lịch sử Việt Nam, Tập 6 (Từ 1858 đến 1896)', 'Công trình nghiên cứu khoa học', 'Viện Sử học Việt Nam', 'Khoa học Xã hội', 2017, 'Phần II: Quá trình phân hóa và thỏa hiệp của triều đình Huế, tr. 84-95.', 'Chính thống - Cấp Quốc gia'),
(3, 'Sách giáo khoa Lịch sử 11', 'Sách giáo khoa Quốc gia', 'Bộ Giáo dục và Đào tạo', 'Giáo dục Việt Nam', 2020, 'Bài 19: Nhân dân Việt Nam kháng chiến chống Pháp xâm lược (1858-1873), tr. 115-118.', 'Chính thống - Cấp Quốc gia'),
(4, 'Lịch sử bang giao Việt Nam cận đại', 'Chuyên khảo lịch sử', 'PGS.TS. Trần Nam Tiến', 'Chính trị quốc gia Sự thật', 2014, 'Chương 3: Các hòa ước giữa nhà Nguyễn và thực dân Pháp 1862-1884, tr. 145-152.', 'Chính thống - Cấp Quốc gia'),
(5, 'Phong trào Cần Vương trong lịch sử Việt Nam', 'Chuyên khảo lịch sử', 'GS. Đinh Xuân Lâm - Đỗ Bang', 'Thuận Hóa', 2001, 'Chương II: Chiếu Cần Vương và sự bùng nổ các cuộc khởi nghĩa, tr. 45-60.', 'Chính thống - Cấp Quốc gia'),
(6, 'Khởi nghĩa Yên Thế (1884-1913)', 'Tư liệu lịch sử địa phương và quốc gia', 'Sở Văn hóa Thể thao và Du lịch Bắc Giang', 'Chính trị quốc gia Sự thật', 2013, 'Phần III: Chiến thuật du kích và các căn cứ Phồn Xương, tr. 112-140.', 'Chính thống - Cấp Quốc gia'),
(7, 'Phan Bội Châu Toàn tập, Tập 3: Tự phán', 'Tự truyện / Hồi ký danh nhân', 'Phan Bội Châu (Chương Thâu sưu tầm, khảo cứu)', 'Thuận Hóa', 2001, 'Phần Đông Du ký và tôn chỉ Hội Duy Tân, tr. 45-78.', 'Chính thống - Cấp Quốc gia'),
(8, 'Phong trào Đông Kinh Nghĩa Thục', 'Công trình nghiên cứu lịch sử văn hóa', 'Nguyễn Hiến Lê', 'Văn hóa Thông tin', 2007, 'Chương II: Tôn chỉ, mục đích và các hoạt động giảng dạy, tr. 32-58.', 'Chính thống - Cấp Quốc gia'),
(9, 'Hồ Chí Minh: Biên niên tiểu sử, Tập 1 (1890 - 1929)', 'Tư liệu chính văn lịch sử', 'Viện Lịch sử Đảng, Học viện Chính trị Quốc gia Hồ Chí Minh', 'Chính trị quốc gia Sự thật', 2016, 'Mục năm 1911: Ngày 5 tháng 6, tr. 42-45.', 'Chính thống - Cấp Quốc gia'),
(10, 'Hồ Chí Minh Toàn tập, Tập 1 (1912 - 1925)', 'Văn kiện chính trị toàn tập', 'Hồ Chí Minh', 'Chính trị quốc gia Sự thật', 2011, 'Văn kiện: Yêu sách của nhân dân An Nam (18/6/1919), tr. 435-438.', 'Chính thống - Cấp Quốc gia'),
(11, 'Hồ Chí Minh: Tiểu sử', 'Tiểu sử lãnh tụ chuẩn quốc gia', 'Ban Tuyên giáo Trung ương', 'Chính trị quốc gia Sự thật', 2020, 'Chương 2: Tìm thấy con đường cứu nước, giải phóng dân tộc (1911-1920), tr. 68-75.', 'Chính thống - Cấp Quốc gia'),
(12, 'Lịch sử Đảng Cộng sản Việt Nam, Tập 1 (1930 - 1954)', 'Lịch sử Đảng chuẩn', 'Hội đồng Trung ương chỉ đạo biên soạn Giáo trình quốc gia', 'Chính trị quốc gia Sự thật', 2018, 'Chương I: Sự ra đời của Đảng Cộng sản Việt Nam, tr. 55-65.', 'Chính thống - Cấp Quốc gia'),
(13, 'Hồ Chí Minh Toàn tập, Tập 2 (1926 - 1930)', 'Văn kiện chính trị toàn tập', 'Hồ Chí Minh', 'Chính trị quốc gia Sự thật', 2011, 'Tác phẩm: Đường Kách mệnh (1927), tr. 279-340.', 'Chính thống - Cấp Quốc gia'),
(14, 'Văn kiện Đảng toàn tập, Tập 2 (1930)', 'Văn kiện Đảng gốc', 'Ban Nghiên cứu Lịch sử Đảng Trung ương', 'Chính trị quốc gia Sự thật', 2002, 'Văn kiện: Chánh cương vắn tắt, Sách lược vắn tắt của Đảng, tr. 1-15.', 'Chính thống - Cấp Quốc gia'),
(15, 'Sách giáo khoa Lịch sử 12 (Chương trình chuẩn)', 'Sách giáo khoa Quốc gia', 'Bộ Giáo dục và Đào tạo', 'Giáo dục Việt Nam', 2021, 'Bài 13: Phong trào dân tộc dân chủ ở Việt Nam từ năm 1925 đến năm 1930, tr. 82-84.', 'Chính thống - Cấp Quốc gia'),
(16, 'Lịch sử giai cấp công nhân Việt Nam, Tập 1', 'Công trình nghiên cứu lịch sử', 'Viện Sử học', 'Khoa học Xã hội', 2012, 'Chương IV: Phong trào Xô viết Nghệ Tĩnh 1930-1931, tr. 145-180.', 'Chính thống - Cấp Quốc gia'),
(17, 'Văn kiện Đảng toàn tập, Tập 2 (1930)', 'Văn kiện Đảng gốc', 'Ban Chấp hành Trung ương Đảng', 'Chính trị quốc gia Sự thật', 2002, 'Luận cương chánh trị của Đảng Cộng sản Đông Dương (10/1930), tr. 88-114.', 'Chính thống - Cấp Quốc gia'),
(18, 'Lịch sử Đảng Cộng sản Việt Nam, Tập 1 (1930 - 1954)', 'Giáo trình quốc gia', 'Hội đồng Trung ương chỉ đạo biên soạn Giáo trình quốc gia', 'Chính trị quốc gia Sự thật', 2018, 'Chương III: Phong trào dân chủ 1936-1939, tr. 210-245.', 'Chính thống - Cấp Quốc gia'),
(19, 'Lịch sử Nam Bộ kháng chiến, Tập 1 (1945 - 1954)', 'Công trình tổng kết lịch sử cấp nhà nước', 'Hội đồng chỉ đạo biên soạn Lịch sử Nam Bộ kháng chiến', 'Chính trị quốc gia Sự thật', 2011, 'Phần mở đầu: Khởi nghĩa Nam Kỳ và sự ra đời của lá cờ đỏ sao vàng, tr. 95-108.', 'Chính thống - Cấp Quốc gia'),
(20, 'Bác Hồ ở Pác Bó', 'Hồi ký và khảo cứu lịch sử', 'Ban Tuyên giáo Tỉnh ủy Cao Bằng', 'Kim Đồng', 2015, 'Chương I: Bước chân qua mốc 108 và căn lán Pác Bó, tr. 18-35.', 'Chính thống - Cấp Quốc gia'),
(21, 'Văn kiện Đảng toàn tập, Tập 7 (1940 - 1945)', 'Văn kiện Đảng gốc', 'Ban Chấp hành Trung ương Đảng', 'Chính trị quốc gia Sự thật', 2000, 'Nghị quyết của Hội nghị Ban Chấp hành Trung ương Đảng lần thứ 8, tr. 99-135.', 'Chính thống - Cấp Quốc gia'),
(22, 'Lịch sử Quân đội nhân dân Việt Nam, Tập 1', 'Lịch sử quân sự cấp quốc gia', 'Viện Lịch sử Quân sự Việt Nam', 'Quân đội Nhân dân', 2014, 'Chương II: Đội Việt Nam Tuyên truyền Giải phóng quân ra đời và những chiến công đầu tiên, tr. 75-92.', 'Chính thống - Cấp Quốc gia'),
(23, 'Cách mạng Tháng Tám 1945 - Thắng lợi của ý chí độc lập tự do', 'Công trình tổng kết lịch sử', 'Viện Lịch sử Quân sự Việt Nam', 'Quân đội Nhân dân', 2015, 'Chương IV: Quốc dân Đại hội Tân Trào và Lệnh Tổng khởi nghĩa, tr. 140-162.', 'Chính thống - Cấp Quốc gia'),
(24, 'Lịch sử Thủ đô Hà Nội', 'Lịch sử địa phương chuẩn', 'GS. Trần Huy Liệu (Chủ biên)', 'Sử học', 2010, 'Phần Cách mạng Tháng Tám: Ngày 19 tháng Tám lịch sử tại Hà Nội, tr. 320-345.', 'Chính thống - Cấp Quốc gia'),
(25, 'Tuyên ngôn Độc lập năm 1945 - Giá trị lịch sử và thời đại', 'Văn kiện lập quốc cấp nhà nước', 'Viện Hàn lâm Khoa học Xã hội Việt Nam', 'Chính trị quốc gia Sự thật', 2015, 'Toàn văn bản Tuyên ngôn Độc lập ngày 2/9/1945 và khảo luận lịch sử, tr. 15-40.', 'Chính thống - Cấp Quốc gia'),
(26, 'Hồ Chí Minh Toàn tập, Tập 4 (1945 - 1946)', 'Văn kiện chính trị toàn tập', 'Hồ Chí Minh', 'Chính trị quốc gia Sự thật', 2011, 'Lời kêu gọi toàn quốc kháng chiến (19/12/1946), tr. 534-535.', 'Chính thống - Cấp Quốc gia'),
(27, 'Lịch sử cuộc kháng chiến chống thực dân Pháp (1945 - 1954), Tập 1', 'Lịch sử chiến tranh toàn diện', 'Viện Lịch sử Quân sự Việt Nam', 'Quân đội Nhân dân', 2013, 'Chương IV: Chiến dịch phản công Việt Bắc Thu Đông 1947, tr. 180-215.', 'Chính thống - Cấp Quốc gia'),
(28, 'Chiến dịch Biên giới Thu Đông 1950', 'Tư liệu tổng kết chiến dịch quân sự', 'Viện Lịch sử Quân sự Việt Nam', 'Quân đội Nhân dân', 2010, 'Toàn tập diễn biến chiến dịch và trận đánh Đông Khê, tr. 88-132.', 'Chính thống - Cấp Quốc gia'),
(29, 'Điện Biên Phủ - Điểm hẹn lịch sử (Hồi ký)', 'Hồi ký tướng lĩnh chỉ huy tối cao', 'Đại tướng Võ Nguyên Giáp (Hữu Mai thể hiện)', 'Quân đội Nhân dân', 2004, 'Chương VII: Chiều mùng 7 tháng 5 định mệnh và khúc ca chiến thắng, tr. 350-420.', 'Chính thống - Cấp Quốc gia'),
(30, 'Tổng hành dinh trong Mùa Xuân toàn thắng', 'Hồi ký lịch sử quân sự', 'Đại tướng Võ Nguyên Giáp', 'Chính trị quốc gia Sự thật', 2005, 'Chương V: Chiến dịch giải phóng Sài Gòn mang tên Bác, tr. 220-275.', 'Chính thống - Cấp Quốc gia');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhan_vat`
--

CREATE TABLE `nhan_vat` (
  `ma_nhan_vat` int(11) NOT NULL,
  `ma_dia_diem` int(11) DEFAULT NULL,
  `ten_nhan_vat` varchar(100) NOT NULL,
  `loai_nhan_vat` varchar(50) DEFAULT 'nhan_chung',
  `loi_thoai` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nhan_vat`
--

INSERT INTO `nhan_vat` (`ma_nhan_vat`, `ma_dia_diem`, `ten_nhan_vat`, `loai_nhan_vat`, `loi_thoai`) VALUES
(1, 1, 'Người dân bến cảng', 'witness', 'Tôi còn nhớ chiếc tàu buôn Amiral Latouche-Tréville rời cảng Sài Gòn mang theo người thanh niên Văn Ba giàu lòng yêu nước.'),
(2, 2, 'Cán bộ liên lạc quốc tế', 'witness', 'Đồng chí Nguyễn Ái Quốc đã triệu tập đại biểu Đông Dương Cộng sản Đảng và An Nam Cộng sản Đảng đến Hương Cảng vào dịp Tết năm 1930.'),
(3, 3, 'Tự vệ đỏ Nghệ Tĩnh', 'witness', 'Hàng vạn nông dân Hưng Nguyên, Bến Thủy biểu tình thị uy đòi quyền sống, lập nên chính quyền Xô viết tự quản.'),
(4, 4, 'Đồng chí dẫn đường người Tày', 'witness', 'Sáng 28 Tết năm ấy, sương mù giăng kín núi rừng biên giới. Tôi vinh dự được dẫn đường đón Bác bước qua cột mốc 108 trở về đất mẹ sau 30 năm bôn ba...'),
(5, 5, 'Đại biểu Quốc dân Đại hội', 'witness', 'Không khí tại đình Tân Trào hừng hực quyết tâm: Dù hy sinh tới đâu cũng phải kiên quyết giành cho được độc lập!'),
(6, 6, 'Chiến sĩ Tự vệ Thành Hoàng Diệu', 'witness', 'Sáng 19/8/1945, biển cờ đỏ sao vàng rực rỡ tại Nhà Hát Lớn. Toàn dân nhất tề đứng lên biến cuộc mít tinh thành khởi nghĩa giành chính quyền...'),
(7, 7, 'Chiến sĩ Trung đoàn Thủ đô', 'witness', 'Rừng núi Việt Bắc hiểm trở đã chôn vùi binh đoàn dù thiện chiến của giặc Pháp trong Thu - Đông 1947.'),
(8, 8, 'Đại tướng Võ Nguyên Giáp', 'historical_figure', 'Đây là quyết định khó khăn nhất trong cuộc đời chỉ huy của tôi: Hoãn nổ súng, chuyển từ phương châm Đánh nhanh thắng nhanh sang Đánh chắc tiến chắc để bảo toàn lực lượng và bảo đảm chắc thắng...');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhan_vat_lich_su`
--

CREATE TABLE `nhan_vat_lich_su` (
  `ma_nhan_vat` int(11) NOT NULL,
  `ten_nhan_vat` varchar(150) NOT NULL,
  `nam_sinh_mat` varchar(50) DEFAULT NULL,
  `vai_tro` varchar(150) DEFAULT NULL,
  `tieu_su_dong_gop` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `nhan_vat_lich_su`
--

INSERT INTO `nhan_vat_lich_su` (`ma_nhan_vat`, `ten_nhan_vat`, `nam_sinh_mat`, `vai_tro`, `tieu_su_dong_gop`) VALUES
(101, 'Nguyễn Tri Phương', '1800 - 1873', 'Đại thần Tổng đốc quân vụ', 'Danh tướng triều Nguyễn, kiên quyết chống giặc tại mặt trận Đà Nẵng, Gia Định và Hà Nội.'),
(102, 'Phan Thanh Giản', '1796 - 1867', 'Chánh sứ đàm phán triều Nguyễn', 'Đại thần đầu triều, người trực tiếp thương thuyết và ký Hiệp ước Nhâm Tuất 1862.'),
(103, 'Trương Định', '1820 - 1864', 'Thủ lĩnh nghĩa quân Nam Bộ', 'Anh hùng kháng chiến chống thực dân Pháp, được nhân dân tôn vinh Bình Tây Đại nguyên soái.'),
(104, 'Nguyễn Văn Tường', '1824 - 1886', 'Phụ chính đại thần triều Nguyễn', 'Cùng Tôn Thất Thuyết nắm quyền triều chính giai đoạn biến loạn 1883-1885.'),
(105, 'Hàm Nghi (Nguyễn Phúc Ưng Lịch)', '1871 - 1944', 'Hoàng đế thứ 8 triều Nguyễn', 'Vị hoàng đế yêu nước, bất khuất lãnh đạo phong trào Cần Vương chống ách đô hộ Pháp.'),
(106, 'Tôn Thất Thuyết', '1839 - 1913', 'Thượng thư Bộ Binh, đại thần phái chủ chiến', 'Linh hồn chỉ huy cuộc phản công tại kinh thành Huế và phát động phong trào Cần Vương.'),
(107, 'Hoàng Hoa Thám', '1858 - 1913', 'Thủ lĩnh khởi nghĩa Yên Thế', 'Được mệnh danh \'Hùm xám Yên Thế\', lãnh tụ phong trào nông dân kháng chiến chống Pháp tiêu biểu.'),
(108, 'Phan Bội Châu', '1867 - 1940', 'Chí sĩ yêu nước, nhà cách mạng tiền bối', 'Người sáng lập phong trào Đông Du, Việt Nam Quang phục Hội.'),
(109, 'Lương Văn Can', '1854 - 1927', 'Hiệu trưởng Đông Kinh Nghĩa Thục', 'Nhà giáo dục yêu nước, khởi xướng tinh thần doanh thương và canh tân đất nước.'),
(110, 'Hồ Chí Minh (Nguyễn Ái Quốc)', '1890 - 1969', 'Lãnh tụ vĩ đại của dân tộc Việt Nam', 'Người sáng lập Đảng, khai sinh nước Việt Nam Dân chủ Cộng hòa.'),
(111, 'Nguyễn Thái Học', '1902 - 1930', 'Chủ tịch Việt Nam Quốc dân Đảng', 'Lãnh tụ cuộc khởi nghĩa Yên Bái, nêu cao tinh thần bất khuất trước máy chém thực dân.'),
(112, 'Lê Mao', '1903 - 1931', 'Ủy viên Trung ương Đảng, Bí thư Tỉnh ủy Nghệ An', 'Một trong những lãnh đạo nòng cốt của cao trào Xô viết Nghệ - Tĩnh.'),
(113, 'Trần Phú', '1904 - 1931', 'Tổng Bí thư đầu tiên của Đảng', 'Người dự thảo bản Luận cương chính trị tháng 10/1930 với câu nói bất hủ \'Hãy giữ vững chí khí chiến đấu\'.'),
(114, 'Nguyễn Văn Cừ', '1912 - 1941', 'Tổng Bí thư Ban Chấp hành Trung ương Đảng (1938-1940)', 'Tác giả tác phẩm \'Tự chỉ trích\' nổi tiếng, chỉ đạo chuyển hướng chiến lược cách mạng sắc bén.'),
(115, 'Nguyễn Thị Minh Khai', '1910 - 1941', 'Bí thư Thành ủy Sài Gòn - Chợ Lớn', 'Chiến sĩ cộng sản kiên trung tham gia lãnh đạo chuẩn bị Khởi nghĩa Nam Kỳ.'),
(116, 'Trường Chinh (Đặng Xuân Khu)', '1907 - 1988', 'Tổng Bí thư Đảng Cộng sản Đông Dương', 'Nhà lý luận chiến lược xuất sắc của Đảng, được bầu làm Tổng Bí thư tại Hội nghị TW 8.'),
(117, 'Võ Nguyên Giáp', '1911 - 2013', 'Chỉ huy trưởng Mặt trận Biên Giới / Điện Biên Phủ', 'Đại tướng Tổng tư lệnh kiệt xuất của Quân đội nhân dân Việt Nam.'),
(118, 'Nguyễn Khang', '1919 - 1976', 'Chủ tịch Ủy ban Khởi nghĩa Hà Nội', 'Người trực tiếp ra quyết định phát động khởi nghĩa giành chính quyền tại Hà Nội ngày 19/8/1945.'),
(119, 'La Văn Cầu', '1931 - nay', 'Anh hùng Lực lượng Vũ trang Nhân dân', 'Tấm gương dũng cảm nhờ đồng đội chặt cánh tay bị thương tiếp tục ôm bộc phá phá lô cốt Đông Khê.'),
(120, 'Văn Tiến Dũng', '1917 - 2002', 'Tư lệnh Chiến dịch Hồ Chí Minh', 'Đại tướng Quân đội, trực tiếp chỉ huy 5 cánh quân giải phóng Sài Gòn mùa Xuân 1975.'),
(121, 'Bùi Quang Thận', '1948 - 2012', 'Đại đội trưởng Đại đội 4 xe tăng, Lữ đoàn 203', 'Người cắm lá cờ chiến thắng lên nóc Dinh Độc Lập lúc 11h30 ngày 30/4/1975.');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `su_kien_lich_su`
--

CREATE TABLE `su_kien_lich_su` (
  `ma_su_kien` int(11) NOT NULL,
  `ma_dia_diem` int(11) DEFAULT NULL,
  `ten_su_kien` varchar(255) NOT NULL,
  `nam_dien_ra` int(11) NOT NULL,
  `ngay_thang_chi_tiet` varchar(50) DEFAULT NULL,
  `thoi_ky` varchar(50) NOT NULL,
  `tom_tat_dien_bien` text NOT NULL,
  `nguon_trich_dan` text NOT NULL,
  `ma_moc` int(11) DEFAULT NULL,
  `ma_nguon` int(11) DEFAULT NULL,
  `nhan_vat_chinh` varchar(255) DEFAULT NULL,
  `y_nghia_lich_su` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `su_kien_lich_su`
--

INSERT INTO `su_kien_lich_su` (`ma_su_kien`, `ma_dia_diem`, `ten_su_kien`, `nam_dien_ra`, `ngay_thang_chi_tiet`, `thoi_ky`, `tom_tat_dien_bien`, `nguon_trich_dan`, `ma_moc`, `ma_nguon`, `nhan_vat_chinh`, `y_nghia_lich_su`) VALUES
(1, 1, 'Liên quân Pháp - Tây Ban Nha nổ súng tấn công bán đảo Sơn Trà (Đà Nẵng)', 1858, '01/09/1858', '1858 - 1918', 'Sáng 1/9/1858, liên quân Pháp và Tây Ban Nha gồm 14 chiến thuyền nổ súng tấn công bán đảo Sơn Trà, chính thức mở đầu cuộc chiến tranh xâm lược Việt Nam. Quân dân ta dưới sự chỉ huy của Tổng đốc Nguyễn Tri Phương đã anh dũng chặn đánh, thực hiện \'vườn không nhà trống\', giam chân giặc suốt 5 tháng trên bán đảo.', 'Đại cương Lịch sử Việt Nam, Tập 2, GS. Đinh Xuân Lâm (Chủ biên), NXB Giáo dục Việt Nam (2006); Chương I: Cuộc kháng chiến chống thực dân Pháp xâm lược (1858-1884), tr. 15-22.', 1, 1, 'Nguyễn Tri Phương', 'Làm thất bại hoàn toàn kế hoạch \'đánh nhanh thắng nhanh\' của thực dân Pháp ngay từ những ngày đầu.'),
(2, 2, 'Triều đình nhà Nguyễn ký Hiệp ước Nhâm Tuất', 1862, '05/06/1862', '1858 - 1918', 'Triều đình Huế cử Phan Thanh Giản và Lâm Duy Hiệp vào Gia Định ký với đại diện Pháp bản Hiệp ước Nhâm Tuất. Triều đình chấp thuận nhượng ba tỉnh miền Đông Nam Kỳ (Gia Định, Định Tường, Biên Hòa) và đảo Côn Lôn cho Pháp, bồi thường 4 triệu peso chiến phí.', 'Lịch sử Việt Nam, Tập 6 (Từ 1858 đến 1896), Viện Sử học Việt Nam, NXB Khoa học Xã hội (2017); Phần II: Quá trình phân hóa và thỏa hiệp của triều đình Huế, tr. 84-95.', 2, 2, 'Phan Thanh Giản, Lâm Duy Hiệp', 'Hiệp ước bất bình đẳng đầu tiên, bộc lộ sự nhu nhược của triều đình phong kiến và mở đường cho Pháp bành trướng Nam Kỳ.'),
(3, 3, 'Khởi nghĩa Trương Định giương cao cờ Bình Tây Đại nguyên soái', 1864, '20/08/1864', '1858 - 1918', 'Bất chấp lệnh bãi binh của triều đình Huế sau Hiệp ước 1862, Trương Định tuân theo ý nguyện nhân dân nhận danh hiệu \'Bình Tây Đại nguyên soái\', tiếp tục lãnh đạo nghĩa quân đánh Pháp tại Tân Hòa, Gò Công. Đêm 19 rạng ngày 20/8/1864, giặc bao vây căn cứ, ông đã rút gươm tự sát để giữ tròn khí tiết.', 'Sách giáo khoa Lịch sử 11, Bộ Giáo dục và Đào tạo, NXB Giáo dục Việt Nam (2020); Bài 19: Nhân dân Việt Nam kháng chiến chống Pháp xâm lược (1858-1873), tr. 115-118.', 3, 3, 'Trương Định', 'Biểu tượng bất khuất của phong trào kháng chiến chống Pháp tự phát của nhân dân Nam Bộ.'),
(4, 4, 'Triều đình Huế ký Hiệp ước Patenôtre (Giáp Thân)', 1884, '06/06/1884', '1858 - 1918', 'Hiệp ước Patenôtre gồm 19 điều khoản được ký kết giữa đại diện triều đình Huế và đại sứ Pháp. Hiệp ước này chính thức đặt cơ sở bảo hộ lâu dài của Pháp lên toàn bộ lãnh thổ Việt Nam, chia nước ta làm ba kỳ: Bắc Kỳ, Trung Kỳ và Nam Kỳ với các quy chế cai trị khác nhau.', 'Lịch sử bang giao Việt Nam cận đại, PGS.TS. Trần Nam Tiến, NXB Chính trị quốc gia Sự thật (2014); Chương 3: Các hòa ước giữa nhà Nguyễn và thực dân Pháp 1862-1884, tr. 145-152.', 4, 4, 'Nguyễn Văn Tường, Jules Patenôtre', 'Đánh dấu sự đầu hàng hoàn toàn của triều đình phong kiến nhà Nguyễn, biến Việt Nam thành nước thuộc địa nửa phong kiến.'),
(5, 5, 'Vua Hàm Nghi hạ chiếu Cần Vương phát động phong trào phò vua cứu nước', 1885, '13/07/1885', '1858 - 1918', 'Sau cuộc tấn công đồn Mang Cá thất bại tại kinh thành Huế đêm 4 rạng 5/7/1885, Tôn Thất Thuyết phò tá vua trẻ Hàm Nghi chạy ra sơn phòng Tân Sở (Quảng Trị). Ngày 13/7/1885, vua Hàm Nghi ban Chiếu Cần Vương, kêu gọi sĩ phu, văn thân và nhân dân toàn quốc đứng lên đánh Pháp.', 'Phong trào Cần Vương trong lịch sử Việt Nam, GS. Đinh Xuân Lâm - Đỗ Bang, NXB Thuận Hóa (2001); Chương II: Chiếu Cần Vương và sự bùng nổ các cuộc khởi nghĩa, tr. 45-60.', 5, 5, 'Vua Hàm Nghi, Tôn Thất Thuyết', 'Thổi bùng phong trào vũ trang kháng chiến cứu nước sâu rộng theo ý thức hệ phong kiến cuối thế kỷ XIX.'),
(6, 6, 'Khởi nghĩa nông dân Yên Thế do Hoàng Hoa Thám lãnh đạo', 1887, '1887 - 1913', '1858 - 1918', 'Khởi nghĩa nổ ra từ năm 1884 tại vùng núi rừng hiểm trở Yên Thế. Từ năm 1892, dưới sự chỉ huy mưu trí của Đề Thám, nghĩa quân đã dùng lối đánh du kích linh hoạt, buộc thực dân Pháp hai lần phải ký hòa hoãn (1894 và 1897). Phong trào duy trì kiên cường suốt gần 30 năm đến năm 1913.', 'Khởi nghĩa Yên Thế (1884-1913), Sở Văn hóa Thể thao và Du lịch Bắc Giang, NXB Chính trị quốc gia Sự thật (2013); Phần III: Chiến thuật du kích và các căn cứ Phồn Xương, tr. 112-140.', 6, 6, 'Hoàng Hoa Thám (Đề Thám)', 'Phong trào khởi nghĩa vũ trang tự phát của nông dân bền bỉ và oanh liệt nhất trong lịch sử chống Pháp trước 1930.'),
(7, 7, 'Phan Bội Châu sáng lập Hội Duy Tân và phong trào Đông Du', 1904, '05/1904', '1858 - 1918', 'Tháng 5/1904, Phan Bội Châu cùng Cường Để thành lập Hội Duy Tân tại Quảng Nam. Năm 1905, ông sang Nhật Bản mở đầu phong trào Đông Du, đưa khoảng 200 thanh niên yêu nước Việt Nam sang Nhật học tập khoa học, kỹ thuật và quân sự nhằm mưu cầu độc lập dân tộc.', 'Phan Bội Châu Toàn tập, Tập 3: Tự phán, Phan Bội Châu (Chương Thâu sưu tầm, khảo cứu), NXB Thuận Hóa (2001); Phần Đông Du ký và tôn chỉ Hội Duy Tân, tr. 45-78.', 7, 7, 'Phan Bội Châu, Kỳ Ngoại hầu Cường Để', 'Chuyển phong trào cứu nước sang khuynh hướng dân chủ tư sản, mở rộng tầm nhìn cách mạng ra trường quốc tế.'),
(8, 8, 'Phong trào Đông Kinh Nghĩa Thục tại Hà Nội', 1907, '03/1907 - 11/1907', '1858 - 1918', 'Tháng 3/1907, các sĩ phu tiến bộ như Lương Văn Can, Nguyễn Quyền lập trường Đông Kinh Nghĩa Thục dạy học miễn phí, phổ biến chữ Quốc ngữ, truyền bá tư tưởng duy tân, cải cách văn hóa và chấn hưng thực nghiệp. Trường nhanh chóng lan rộng ảnh hưởng trước khi bị Pháp cưỡng bức đóng cửa cuối năm 1907.', 'Phong trào Đông Kinh Nghĩa Thục, Nguyễn Hiến Lê, NXB Văn hóa Thông tin (2007); Chương II: Tôn chỉ, mục đích và các hoạt động giảng dạy, tr. 32-58.', 8, 8, 'Lương Văn Can, Nguyễn Quyền', 'Cuộc vận động văn hóa tiến bộ, đánh thức lòng yêu nước và ý thức tự lực tự cường của nhân dân.'),
(9, 1, 'Nguyễn Tất Thành ra đi tìm đường cứu nước từ Bến Nhà Rồng', 1911, '05/06/1911', '1858 - 1930', 'Ngày 5/6/1911, người thanh niên yêu nước Nguyễn Tất Thành lấy tên Văn Ba xuống con tàu Đô đốc Latouche-Tréville rời bến cảng Nhà Rồng (Sài Gòn) sang phương Tây. Người quyết tâm tìm hiểu những gì ẩn giấu đằng sau khẩu hiệu \'Tự do - Bình đẳng - Bác ái\' để trở về giúp đồng bào.', 'Hồ Chí Minh: Biên niên tiểu sử, Tập 1 (1890 - 1929), Viện Lịch sử Đảng, Học viện Chính trị Quốc gia Hồ Chí Minh, NXB Chính trị quốc gia Sự thật (2016); Mục năm 1911: Ngày 5 tháng 6, tr. 42-45.', 9, 9, 'Nguyễn Tất Thành (Văn Ba)', 'Mở ra bước ngoặt quyết định của lịch sử dân tộc, khởi đầu hành trình tìm ra con đường cứu nước đúng đắn.'),
(10, NULL, 'Nguyễn Ái Quốc gửi Bản Yêu sách của nhân dân An Nam tới Hội nghị Versailles', 1919, '18/06/1919', '1919 - 1930', 'Thay mặt \'Nhóm người Việt Nam yêu nước\' tại Pháp, Nguyễn Ái Quốc gửi bản Yêu sách của nhân dân An Nam gồm 8 điểm tới Hội nghị Versailles. Bản yêu sách đòi chính phủ Pháp thừa nhận quyền tự do, bình đẳng, bãi bỏ chế độ cai trị tàn bạo ở Đông Dương.', 'Hồ Chí Minh Toàn tập, Tập 1 (1912 - 1925), Hồ Chí Minh, NXB Chính trị quốc gia Sự thật (2011); Văn kiện: Yêu sách của nhân dân An Nam (18/6/1919), tr. 435-438.', 10, 10, 'Nguyễn Ái Quốc', 'Lần đầu tiên tiếng nói đòi quyền tự do của nhân dân Việt Nam xuất hiện chính thức trên diễn đàn quốc tế.'),
(11, NULL, 'Nguyễn Ái Quốc bỏ phiếu tán thành Quốc tế Ba và sáng lập Đảng Cộng sản Pháp', 1920, '12/1920', '1919 - 1930', 'Tại Đại hội lần thứ XVIII của Đảng Xã hội Pháp họp ở Tours từ ngày 25 đến 30/12/1920, sau khi nghiên cứu Sơ thảo Luận cương của Lênin về vấn đề dân tộc và thuộc địa, Nguyễn Ái Quốc đã bỏ phiếu tán thành gia nhập Quốc tế thứ Ba và tham gia sáng lập Đảng Cộng sản Pháp.', 'Hồ Chí Minh: Tiểu sử, Ban Tuyên giáo Trung ương, NXB Chính trị quốc gia Sự thật (2020); Chương 2: Tìm thấy con đường cứu nước, giải phóng dân tộc (1911-1920), tr. 68-75.', 11, 11, 'Nguyễn Ái Quốc', 'Đánh dấu bước chuyển biến quyết định từ chủ nghĩa yêu nước chân chính đến chủ nghĩa Mác - Lênin của người.'),
(12, NULL, 'Thành lập Hội Việt Nam Cách mạng Thanh niên tại Quảng Châu', 1925, '06/1925', '1919 - 1930', 'Tháng 6/1925, Nguyễn Ái Quốc thành lập Hội Việt Nam Cách mạng Thanh niên tại Quảng Châu nhằm chuẩn bị về tổ chức và cán bộ cho sự ra đời của Đảng Cộng sản. Cơ quan ngôn luận của Hội là tuần báo Thanh Niên, ra số đầu tiên ngày 21/6/1925.', 'Lịch sử Đảng Cộng sản Việt Nam, Tập 1 (1930 - 1954), Hội đồng Trung ương chỉ đạo biên soạn Giáo trình quốc gia, NXB Chính trị quốc gia Sự thật (2018); Chương I: Sự ra đời của Đảng Cộng sản Việt Nam, tr. 55-65.', 12, 12, 'Nguyễn Ái Quốc, Lê Hồng Sơn, Hồ Tùng Mậu', 'Tổ chức tiền thân trực tiếp đưa lý luận giải phóng dân tộc thâm nhập sâu rộng vào phong trào công nhân và quần chúng.'),
(13, NULL, 'Xuất bản tác phẩm Đường Kách mệnh của Nguyễn Ái Quốc', 1927, 'Đầu năm 1927', '1919 - 1930', 'Đầu năm 1927, Bộ Tuyên truyền của Hội Liên hiệp các dân tộc bị áp bức Á Đông xuất bản tác phẩm \'Đường Kách mệnh\' của Nguyễn Ái Quốc. Cuốn sách tập hợp các bài giảng lý luận cách mạng, xác định rõ vai trò lãnh đạo của Đảng tiên phong, động lực cách mạng là công nông.', 'Hồ Chí Minh Toàn tập, Tập 2 (1926 - 1930), Hồ Chí Minh, NXB Chính trị quốc gia Sự thật (2011); Tác phẩm: Đường Kách mệnh (1927), tr. 279-340.', 13, 13, 'Nguyễn Ái Quốc', 'Cuốn cẩm nang lý luận gối đầu giường truyền bá chủ nghĩa Mác - Lênin vào phong trào cách mạng Việt Nam.'),
(14, 2, 'Hội nghị hợp nhất thành lập Đảng Cộng sản Việt Nam', 1930, '03/02/1930', '1930 - 1945', 'Từ ngày 6/1 đến 7/2/1930 tại Hương Cảng, Nguyễn Ái Quốc chủ trì hội nghị hợp nhất các tổ chức cộng sản (Đông Dương Cộng sản Đảng, An Nam Cộng sản Đảng). Hội nghị quyết định thành lập một chính đảng duy nhất lấy tên Đảng Cộng sản Việt Nam, thông qua Chính cương vắn tắt, Sách lược vắn tắt.', 'Văn kiện Đảng toàn tập, Tập 2 (1930), Ban Nghiên cứu Lịch sử Đảng Trung ương, NXB Chính trị quốc gia Sự thật (2002); Văn kiện: Chánh cương vắn tắt, Sách lược vắn tắt của Đảng, tr. 1-15.', 14, 14, 'Nguyễn Ái Quốc, Trịnh Đình Cửu, Châu Văn Liêm', 'Bước ngoặt vô cùng vĩ đại, chấm dứt thời kỳ khủng hoảng sâu sắc về đường lối cứu nước và giai cấp lãnh đạo.'),
(15, NULL, 'Khởi nghĩa Yên Bái của Việt Nam Quốc dân Đảng', 1930, '09/02/1930', '1930 - 1945', 'Đêm 9/2/1930, khởi nghĩa bùng nổ tại đồn Yên Bái và nhanh chóng lan sang Phú Thọ, Hải Dương, Hà Nội với khẩu hiệu \'Không thành công cũng thành nhân\'. Tuy nhiên do nổ ra thế bị động và thiếu đường lối quần chúng vững chắc, khởi nghĩa nhanh chóng bị thực dân Pháp dập tắt trong bể máu.', 'Sách giáo khoa Lịch sử 12 (Chương trình chuẩn), Bộ Giáo dục và Đào tạo, NXB Giáo dục Việt Nam (2021); Bài 13: Phong trào dân tộc dân chủ ở Việt Nam từ năm 1925 đến năm 1930, tr. 82-84.', 15, 15, 'Nguyễn Thái Học, Phó Đức Chính', 'Khẳng định tinh thần quả cảm chống ngoại xâm, đồng thời khép lại hoàn toàn vai trò lịch sử của khuynh hướng tư sản.'),
(16, 3, 'Đỉnh cao phong trào Xô viết Nghệ - Tĩnh', 1930, '12/09/1930', '1930 - 1945', 'Ngày 12/9/1930, khoảng 8.000 nông dân Hưng Nguyên biểu tình kéo về thành phố Vinh. Địch ném bom đàn áp làm 217 người chết, 125 người bị thương. Làn sóng căm phẫn dâng cao, quần chúng lật đổ chính quyền tay sai ở nhiều huyện, lập nên chính quyền Xô viết tự quản đầu tiên của công nông.', 'Lịch sử giai cấp công nhân Việt Nam, Tập 1, Viện Sử học, NXB Khoa học Xã hội (2012); Chương IV: Phong trào Xô viết Nghệ Tĩnh 1930-1931, tr. 145-180.', 16, 16, 'Nguyễn Phong Sắc, Lê Mao', 'Cuộc tập dượt đầu tiên cho Cách mạng Tháng Tám, khẳng định liên minh công nông dưới sự lãnh đạo của Đảng.'),
(17, NULL, 'Hội nghị Trung ương lần thứ nhất thông qua Luận cương chính trị', 1930, '10/1930', '1930 - 1945', 'Tháng 10/1930, Ban Chấp hành Trung ương Đảng họp Hội nghị lần thứ nhất tại Hương Cảng do Trần Phú chủ trì. Hội nghị quyết định đổi tên Đảng thành Đảng Cộng sản Đông Dương, thông qua Luận cương chính trị và bầu đồng chí Trần Phú làm Tổng Bí thư đầu tiên.', 'Văn kiện Đảng toàn tập, Tập 2 (1930), Ban Chấp hành Trung ương Đảng, NXB Chính trị quốc gia Sự thật (2002); Luận cương chánh trị của Đảng Cộng sản Đông Dương (10/1930), tr. 88-114.', 17, 17, 'Trần Phú', 'Xác định rõ tính chất cách mạng tư sản dân quyền và phương hướng tiến lên chủ nghĩa xã hội ở Đông Dương.'),
(18, NULL, 'Phong trào Dân chủ 1936 - 1939 đòi tự do, dân sinh, dân chủ', 1936, '1936 - 1939', '1930 - 1945', 'Nắm bắt sự thay đổi của tình hình quốc tế và Mặt trận Nhân dân Pháp lên cầm quyền, Đảng ta đã chuyển hướng đấu tranh, kết hợp hợp pháp và nửa hợp pháp. Phong trào Đông Dương Đại hội nổ ra rầm rộ, bãi công, biểu tình và báo chí công khai đòi quyền tự do dân chủ, cải thiện đời sống.', 'Lịch sử Đảng Cộng sản Việt Nam, Tập 1 (1930 - 1954), Hội đồng Trung ương chỉ đạo biên soạn Giáo trình quốc gia, NXB Chính trị quốc gia Sự thật (2018); Chương III: Phong trào dân chủ 1936-1939, tr. 210-245.', 18, 18, 'Lê Hồng Phong, Hà Huy Tập, Nguyễn Văn Cừ', 'Cuộc tập dượt thứ hai đưa chủ nghĩa Mác - Lênin phổ biến sâu rộng trong đông đảo quần chúng nhân dân thành thị và nông thôn.'),
(19, NULL, 'Khởi nghĩa Bắc Sơn và Khởi nghĩa Nam Kỳ bùng nổ', 1940, '27/09/1940 & 23/11/1940', '1930 - 1945', 'Khi phát xít Nhật xâm lược Đông Dương, nhân dân Bắc Sơn đã nổi dậy đánh chiếm đồn Mỏ Nhài ngày 27/9/1940, thành lập Đội du kích Bắc Sơn. Tiếp đó đêm 22 rạng 23/11/1940, Khởi nghĩa Nam Kỳ bùng nổ rung chuyển khắp Nam Bộ. Lá cờ đỏ sao vàng năm cánh lần đầu tiên xuất hiện trong các cuộc tuần hành.', 'Lịch sử Nam Bộ kháng chiến, Tập 1 (1945 - 1954), Hội đồng chỉ đạo biên soạn Lịch sử Nam Bộ kháng chiến, NXB Chính trị quốc gia Sự thật (2011); Phần mở đầu: Khởi nghĩa Nam Kỳ và sự ra đời của lá cờ đỏ sao vàng, tr. 95-108.', 19, 19, 'Chu Văn Tấn, Phan Đăng Lưu, Nguyễn Thị Minh Khai', 'Tiếng súng báo hiệu thời kỳ đấu tranh vũ trang giải phóng dân tộc mới, khai sinh biểu tượng Quốc kỳ thiêng liêng.'),
(20, 4, 'Lãnh tụ Nguyễn Ái Quốc về nước tại Pác Bó trực tiếp lãnh đạo cách mạng', 1941, '28/01/1941', '1930 - 1945', 'Sau 30 năm bôn ba tìm đường cứu nước, ngày 28/1/1941 (mùng 2 Tết Tân Tỵ), lãnh tụ Nguyễn Ái Quốc vượt qua mốc 108 biên giới Việt - Trung về đến hang Pác Bó. Tại đây, Người đã trực tiếp chỉ đạo xây dựng căn cứ địa, mở lớp huấn luyện chính trị, dịch cuốn Lịch sử Đảng Cộng sản Liên Xô làm tài liệu học tập.', 'Bác Hồ ở Pác Bó, Ban Tuyên giáo Tỉnh ủy Cao Bằng, NXB Kim Đồng (2015); Chương I: Bước chân qua mốc 108 và căn lán Pác Bó, tr. 18-35.', 20, 20, 'Nguyễn Ái Quốc (Hồ Chí Minh), Đặng Văn Cáp, Lê Quảng Ba', 'Chấm dứt thời kỳ lãnh đạo từ xa, cách mạng Việt Nam trực tiếp đón nhận sự chèo lái của vị thuyền trưởng thiên tài.'),
(21, NULL, 'Hội nghị Trung ương 8 và thành lập Mặt trận Việt Minh', 1941, '19/05/1941', '1930 - 1945', 'Từ ngày 10 đến 19/5/1941, Hội nghị lần thứ 8 Ban Chấp hành Trung ương Đảng họp tại Pác Bó dưới sự chủ trì của Nguyễn Ái Quốc. Hội nghị quyết định đặt nhiệm vụ giải phóng dân tộc lên hàng đầu trên hết, thành lập Việt Nam Độc lập Đồng minh (Mặt trận Việt Minh) ngày 19/5/1941 và chuẩn bị khởi nghĩa vũ trang.', 'Văn kiện Đảng toàn tập, Tập 7 (1940 - 1945), Ban Chấp hành Trung ương Đảng, NXB Chính trị quốc gia Sự thật (2000); Nghị quyết của Hội nghị Ban Chấp hành Trung ương Đảng lần thứ 8, tr. 99-135.', 21, 21, 'Nguyễn Ái Quốc, Trường Chinh, Hoàng Văn Thụ', 'Hoàn chỉnh sự chuyển hướng chỉ đạo chiến lược cách mạng, quy tụ sức mạnh toàn dân tộc vào ngọn cờ Việt Minh.'),
(22, NULL, 'Thành lập Đội Việt Nam Tuyên truyền Giải phóng quân', 1944, '22/12/1944', '1930 - 1945', 'Thực hiện chỉ thị của Lãnh tụ Hồ Chí Minh, ngày 22/12/1944, Đội Việt Nam Tuyên truyền Giải phóng quân gồm 34 chiến sĩ được thành lập tại khu rừng giữa hai tổng Hoàng Hoa Thám và Trần Hưng Đạo. Đồng chí Võ Nguyên Giáp trực tiếp chỉ huy, ngay sau đó đánh thắng giòn giã hai trận Phai Khắt và Nà Ngần.', 'Lịch sử Quân đội nhân dân Việt Nam, Tập 1, Viện Lịch sử Quân sự Việt Nam, NXB Quân đội Nhân dân (2014); Chương II: Đội Việt Nam Tuyên truyền Giải phóng quân ra đời và những chiến công đầu tiên, tr. 75-92.', 22, 22, 'Võ Nguyên Giáp, Hoàng Sâm', 'Đánh dấu sự ra đời của lực lượng quân đội cách mạng chính quy đầu tiên, tiền thân vẻ vang của Quân đội Nhân dân Việt Nam.'),
(23, 5, 'Quốc dân Đại hội Tân Trào phát lệnh Tổng khởi nghĩa', 1945, '16/08/1945', '1930 - 1945', 'Chiều 16/8/1945, Đại hội Quốc dân khai mạc tại đình Tân Trào với sự tham dự của hơn 60 đại biểu đại diện cho ba kỳ và các đoàn thể kiều bào. Đại hội nhất trí thông qua lệnh Tổng khởi nghĩa giành chính quyền, 10 chính sách lớn của Việt Minh và bầu Ủy ban Dân tộc giải phóng do Hồ Chí Minh làm Chủ tịch.', 'Cách mạng Tháng Tám 1945 - Thắng lợi của ý chí độc lập tự do, Viện Lịch sử Quân sự Việt Nam, NXB Quân đội Nhân dân (2015); Chương IV: Quốc dân Đại hội Tân Trào và Lệnh Tổng khởi nghĩa, tr. 140-162.', 23, 23, 'Hồ Chí Minh, Trường Chinh, Võ Nguyên Giáp', 'Thể hiện khối đại đoàn kết toàn dân tộc và ý chí sắt đá: Dù hy sinh tới đâu cũng phải kiên quyết giành cho được độc lập.'),
(24, NULL, 'Khởi nghĩa giành chính quyền thắng lợi ở Hà Nội', 1945, '19/08/1945', '1930 - 1945', 'Sáng 19/8/1945, hàng chục vạn quần chúng nhân dân thủ đô mít tinh tại Nhà hát Lớn rồi biến thành cuộc biểu tình vũ trang thị uy. Quần chúng dưới sự dẫn đầu của các đội tự vệ xung phong chia làm nhiều cánh đánh chiếm Phủ Khâm sai Bắc Bộ, Trại Bảo an binh, Sở Cảnh sát, giành toàn bộ chính quyền tại Hà Nội.', 'Lịch sử Thủ đô Hà Nội, GS. Trần Huy Liệu (Chủ biên), NXB Sử học (2010); Phần Cách mạng Tháng Tám: Ngày 19 tháng Tám lịch sử tại Hà Nội, tr. 320-345.', 24, 24, 'Nguyễn Khang, Trần Đình Long, Lê Trọng Nghĩa', 'Thắng lợi quyết định ở trái tim cả nước, cổ vũ mạnh mẽ và tạo hiệu ứng domino cho các tỉnh trên toàn quốc khởi nghĩa thắng lợi.'),
(25, 6, 'Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập khai sinh nước VNDCCH', 1945, '02/09/1945', '1930 - 1945', 'Chiều ngày 2/9/1945, trước hơn 50 vạn đồng bào tại Quảng trường Ba Đình, Chủ tịch Hồ Chí Minh thay mặt Chính phủ lâm thời trang nghiêm đọc bản Tuyên ngôn Độc lập, tuyên bố với quốc dân và thế giới: Nước Việt Nam Dân chủ Cộng hòa ra đời, thoát khỏi xiềng xích thực dân, phát xít và phong kiến.', 'Tuyên ngôn Độc lập năm 1945 - Giá trị lịch sử và thời đại, Viện Hàn lâm Khoa học Xã hội Việt Nam, NXB Chính trị quốc gia Sự thật (2015); Toàn văn bản Tuyên ngôn Độc lập ngày 2/9/1945 và khảo luận lịch sử, tr. 15-40.', 25, 25, 'Chủ tịch Hồ Chí Minh', 'Văn kiện lập quốc thiêng liêng, mở ra kỷ nguyên mới - kỷ nguyên độc lập, tự do và chủ nghĩa xã hội của dân tộc Việt Nam.'),
(26, NULL, 'Chủ tịch Hồ Chí Minh ra Lời kêu gọi Toàn quốc kháng chiến', 1946, '19/12/1946', '1945 - 1954', 'Trước dã tâm cướp nước ta một lần nữa của thực dân Pháp sau tối hậu thư ngày 18/12, đêm 19/12/1946, Chủ tịch Hồ Chí Minh ra Lời kêu gọi Toàn quốc kháng chiến: \'Chúng ta thà hy sinh tất cả, chứ nhất định không chịu mất nước, nhất định không chịu làm nô lệ\'. Pháo đài Láng nổ súng phát lệnh kháng chiến bùng nổ.', 'Hồ Chí Minh Toàn tập, Tập 4 (1945 - 1946), Hồ Chí Minh, NXB Chính trị quốc gia Sự thật (2011); Lời kêu gọi toàn quốc kháng chiến (19/12/1946), tr. 534-535.', 26, 26, 'Chủ tịch Hồ Chí Minh, Võ Nguyên Giáp', 'Khơi dậy hào khí non sông, mở đầu cuộc kháng chiến trường kỳ, toàn dân, toàn diện, tự lực cánh sinh chống thực dân Pháp.'),
(27, 7, 'Chiến thắng Việt Bắc Thu - Đông 1947', 1947, '07/10/1947 - 19/12/1947', '1945 - 1954', 'Pháp huy động hơn 12.000 quân tinh nhuệ mở cuộc hành quân Léa tấn công lên căn cứ Việt Bắc hòng tiêu diệt cơ quan đầu não kháng chiến. Quân dân ta với các trận phục kích oanh liệt tại Đoan Hùng, đèo Bông Lau, sông Lô đã đánh tan hai gọng kìm thủy - bộ của địch, tiêu diệt hơn 6.000 tên giặc.', 'Lịch sử cuộc kháng chiến chống thực dân Pháp (1945 - 1954), Tập 1, Viện Lịch sử Quân sự Việt Nam, NXB Quân đội Nhân dân (2013); Chương IV: Chiến dịch phản công Việt Bắc Thu Đông 1947, tr. 180-215.', 27, 27, 'Võ Nguyên Giáp', 'Đập tan chiến lược \'đánh nhanh thắng nhanh\' của Pháp, bảo vệ an toàn đầu não kháng chiến và giữ vững căn cứ địa Việt Bắc.'),
(28, NULL, 'Chiến dịch Biên Giới Thu - Đông 1950', 1950, '16/09/1950 - 22/10/1950', '1945 - 1954', 'Quân ta mở chiến dịch Biên Giới, tấn công cứ điểm Đông Khê mở màn ngày 16/9. Chủ tịch Hồ Chí Minh trực tiếp lên đài quan sát chỉ đạo mặt trận. Quân ta tiêu diệt và bắt sống hai binh đoàn thiện chiến Le Page và Charton, giải phóng dải biên giới Việt - Trung dài 750km với 35 vạn dân.', 'Chiến dịch Biên giới Thu Đông 1950, Viện Lịch sử Quân sự Việt Nam, NXB Quân đội Nhân dân (2010); Toàn tập diễn biến chiến dịch và trận đánh Đông Khê, tr. 88-132.', 28, 28, 'Chủ tịch Hồ Chí Minh, Võ Nguyên Giáp, La Văn Cầu', 'Chiến dịch tiến công quy mô lớn đầu tiên của ta, giành quyền chủ động chiến lược trên chiến trường chính Bắc Bộ.'),
(29, 8, 'Chiến thắng lịch sử Điện Biên Phủ', 1954, '13/03/1954 - 07/05/1954', '1945 - 1954', 'Chiến dịch diễn ra qua 3 đợt trong suốt 56 ngày đêm \'khoét núi, ngủ hầm, mưa dầm, cơm vắt\'. Đại tướng Võ Nguyên Giáp đưa ra quyết định lịch sử chuyển phương châm từ \'Đánh nhanh thắng nhanh\' sang \'Đánh chắc tiến chắc\'. Lúc 17h30 ngày 7/5/1954, cờ Quyết chiến Quyết thắng tung bay trên nóc hầm De Castries, toàn bộ tập đoàn cứ điểm bị tiêu diệt.', 'Điện Biên Phủ - Điểm hẹn lịch sử (Hồi ký), Đại tướng Võ Nguyên Giáp (Hữu Mai thể hiện), NXB Quân đội Nhân dân (2004); Chương VII: Chiều mùng 7 tháng 5 định mệnh và khúc ca chiến thắng, tr. 350-420.', 29, 29, 'Đại tướng Võ Nguyên Giáp, Tướng De Castries', 'Thắng lợi \'lừng lẫy năm châu, chấn động địa cầu\', đập tan kế hoạch Nava, buộc Pháp phải ký Hiệp định Giơ-ne-vơ chấm dứt chiến tranh xâm lược.'),
(30, NULL, 'Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam', 1975, '26/04/1975 - 30/04/1975', '1954 - 1975', '17h ngày 26/4/1975, Chiến dịch Hồ Chí Minh nổ súng với 5 cánh quân tiến công đồng loạt vào giải phóng Sài Gòn. Đúng 10h45 ngày 30/4/1975, xe tăng 390 húc đổ cổng chính và xe tăng 843 tiến vào sân Dinh Độc Lập. 11h30, lá cờ Mặt trận Dân tộc Giải phóng tung bay trên nóc dinh, Tổng thống Dương Văn Minh tuyên bố đầu hàng không điều kiện.', 'Tổng hành dinh trong Mùa Xuân toàn thắng, Đại tướng Võ Nguyên Giáp, NXB Chính trị quốc gia Sự thật (2005); Chương V: Chiến dịch giải phóng Sài Gòn mang tên Bác, tr. 220-275.', 30, 30, 'Đại tướng Văn Tiến Dũng, Bùi Quang Thận, Dương Văn Minh', 'Thắng lợi vĩ đại nhất của lịch sử dân tộc trong thế kỷ XX, thu non sông về một mối, mở ra kỷ nguyên độc lập, thống nhất và phát triển cả nước.');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tien_do_choi`
--

CREATE TABLE `tien_do_choi` (
  `ma_tien_do` int(11) NOT NULL,
  `ma_nguoi_dung` int(11) DEFAULT NULL,
  `ma_dia_diem_hien_tai` int(11) DEFAULT 1,
  `nam_mo_khoa_cao_nhat` int(11) DEFAULT 1914,
  `diem_tri_thuc` int(11) DEFAULT 0,
  `danh_sach_dia_diem_da_mo` text DEFAULT NULL,
  `thoi_gian_cap_nhat` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `du_lieu_nhiem_vu` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `tien_do_choi`
--


-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `tui_do_nguoi_choi`
--

CREATE TABLE `tui_do_nguoi_choi` (
  `ma_tui_do` int(11) NOT NULL,
  `ma_nguoi_dung` int(11) DEFAULT NULL,
  `ma_manh_moi` int(11) DEFAULT NULL,
  `thoi_gian_thu_thap` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `tui_do_nguoi_choi`
--


--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `cau_hoi_on_tap`
--
ALTER TABLE `cau_hoi_on_tap`
  ADD PRIMARY KEY (`ma_cau_hoi`),
  ADD KEY `ma_su_kien` (`ma_su_kien`);

--
-- Chỉ mục cho bảng `dia_diem`
--
ALTER TABLE `dia_diem`
  ADD PRIMARY KEY (`ma_dia_diem`);

--
-- Chỉ mục cho bảng `manh_moi`
--
ALTER TABLE `manh_moi`
  ADD PRIMARY KEY (`ma_manh_moi`),
  ADD KEY `ma_su_kien` (`ma_su_kien`),
  ADD KEY `ma_nhan_vat` (`ma_nhan_vat`);

--
-- Chỉ mục cho bảng `moc_lich_su`
--
ALTER TABLE `moc_lich_su`
  ADD PRIMARY KEY (`ma_moc`),
  ADD KEY `idx_nam` (`nam`);

--
-- Chỉ mục cho bảng `nguoi_dung`
--
ALTER TABLE `nguoi_dung`
  ADD PRIMARY KEY (`ma_nguoi_dung`),
  ADD UNIQUE KEY `ten_dang_nhap` (`ten_dang_nhap`);

--
-- Chỉ mục cho bảng `nguon_lich_su`
--
ALTER TABLE `nguon_lich_su`
  ADD PRIMARY KEY (`ma_nguon`);

--
-- Chỉ mục cho bảng `nhan_vat`
--
ALTER TABLE `nhan_vat`
  ADD PRIMARY KEY (`ma_nhan_vat`),
  ADD KEY `ma_dia_diem` (`ma_dia_diem`);

--
-- Chỉ mục cho bảng `nhan_vat_lich_su`
--
ALTER TABLE `nhan_vat_lich_su`
  ADD PRIMARY KEY (`ma_nhan_vat`),
  ADD KEY `idx_ten_nhan_vat` (`ten_nhan_vat`);

--
-- Chỉ mục cho bảng `su_kien_lich_su`
--
ALTER TABLE `su_kien_lich_su`
  ADD PRIMARY KEY (`ma_su_kien`),
  ADD KEY `ma_dia_diem` (`ma_dia_diem`),
  ADD KEY `ma_moc` (`ma_moc`),
  ADD KEY `ma_nguon` (`ma_nguon`);

--
-- Chỉ mục cho bảng `tien_do_choi`
--
ALTER TABLE `tien_do_choi`
  ADD PRIMARY KEY (`ma_tien_do`),
  ADD UNIQUE KEY `ma_nguoi_dung` (`ma_nguoi_dung`),
  ADD KEY `ma_dia_diem_hien_tai` (`ma_dia_diem_hien_tai`);

--
-- Chỉ mục cho bảng `tui_do_nguoi_choi`
--
ALTER TABLE `tui_do_nguoi_choi`
  ADD PRIMARY KEY (`ma_tui_do`),
  ADD KEY `ma_nguoi_dung` (`ma_nguoi_dung`),
  ADD KEY `ma_manh_moi` (`ma_manh_moi`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `cau_hoi_on_tap`
--
ALTER TABLE `cau_hoi_on_tap`
  MODIFY `ma_cau_hoi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT cho bảng `dia_diem`
--
ALTER TABLE `dia_diem`
  MODIFY `ma_dia_diem` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT cho bảng `manh_moi`
--
ALTER TABLE `manh_moi`
  MODIFY `ma_manh_moi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT cho bảng `moc_lich_su`
--
ALTER TABLE `moc_lich_su`
  MODIFY `ma_moc` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT cho bảng `nguoi_dung`
--
ALTER TABLE `nguoi_dung`
  MODIFY `ma_nguoi_dung` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT cho bảng `nguon_lich_su`
--
ALTER TABLE `nguon_lich_su`
  MODIFY `ma_nguon` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT cho bảng `nhan_vat`
--
ALTER TABLE `nhan_vat`
  MODIFY `ma_nhan_vat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT cho bảng `nhan_vat_lich_su`
--
ALTER TABLE `nhan_vat_lich_su`
  MODIFY `ma_nhan_vat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=122;

--
-- AUTO_INCREMENT cho bảng `su_kien_lich_su`
--
ALTER TABLE `su_kien_lich_su`
  MODIFY `ma_su_kien` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT cho bảng `tien_do_choi`
--
ALTER TABLE `tien_do_choi`
  MODIFY `ma_tien_do` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT cho bảng `tui_do_nguoi_choi`
--
ALTER TABLE `tui_do_nguoi_choi`
  MODIFY `ma_tui_do` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `cau_hoi_on_tap`
--
ALTER TABLE `cau_hoi_on_tap`
  ADD CONSTRAINT `cau_hoi_on_tap_ibfk_1` FOREIGN KEY (`ma_su_kien`) REFERENCES `su_kien_lich_su` (`ma_su_kien`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `manh_moi`
--
ALTER TABLE `manh_moi`
  ADD CONSTRAINT `manh_moi_ibfk_1` FOREIGN KEY (`ma_su_kien`) REFERENCES `su_kien_lich_su` (`ma_su_kien`) ON DELETE CASCADE,
  ADD CONSTRAINT `manh_moi_ibfk_2` FOREIGN KEY (`ma_nhan_vat`) REFERENCES `nhan_vat` (`ma_nhan_vat`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `nhan_vat`
--
ALTER TABLE `nhan_vat`
  ADD CONSTRAINT `nhan_vat_ibfk_1` FOREIGN KEY (`ma_dia_diem`) REFERENCES `dia_diem` (`ma_dia_diem`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `su_kien_lich_su`
--
ALTER TABLE `su_kien_lich_su`
  ADD CONSTRAINT `su_kien_lich_su_ibfk_1` FOREIGN KEY (`ma_dia_diem`) REFERENCES `dia_diem` (`ma_dia_diem`) ON DELETE SET NULL,
  ADD CONSTRAINT `su_kien_lich_su_ibfk_2` FOREIGN KEY (`ma_moc`) REFERENCES `moc_lich_su` (`ma_moc`) ON DELETE SET NULL,
  ADD CONSTRAINT `su_kien_lich_su_ibfk_3` FOREIGN KEY (`ma_nguon`) REFERENCES `nguon_lich_su` (`ma_nguon`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `tien_do_choi`
--
ALTER TABLE `tien_do_choi`
  ADD CONSTRAINT `tien_do_choi_ibfk_1` FOREIGN KEY (`ma_nguoi_dung`) REFERENCES `nguoi_dung` (`ma_nguoi_dung`) ON DELETE CASCADE,
  ADD CONSTRAINT `tien_do_choi_ibfk_2` FOREIGN KEY (`ma_dia_diem_hien_tai`) REFERENCES `dia_diem` (`ma_dia_diem`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `tui_do_nguoi_choi`
--
ALTER TABLE `tui_do_nguoi_choi`
  ADD CONSTRAINT `tui_do_nguoi_choi_ibfk_1` FOREIGN KEY (`ma_nguoi_dung`) REFERENCES `nguoi_dung` (`ma_nguoi_dung`) ON DELETE CASCADE,
  ADD CONSTRAINT `tui_do_nguoi_choi_ibfk_2` FOREIGN KEY (`ma_manh_moi`) REFERENCES `manh_moi` (`ma_manh_moi`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
