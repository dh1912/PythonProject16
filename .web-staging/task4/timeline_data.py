"""Four historical timeline quests with evidence and three quiz questions each."""
from .quest_system import Clue


def _clues(prefix, titles, details, source):
    return [Clue(f"{prefix}_{i}", title, "tư liệu lịch sử", detail, source, i)
            for i, (title, detail) in enumerate(zip(titles, details))]


def _questions(prefix, data):
    """
    Chuyển dữ liệu câu hỏi thành danh sách dict có cấu trúc nhất quán.
    Hỗ trợ 2 format tuple:
    - Format cũ (5 phần tử): (question, options, answer_index, explanation, source)
      -> points mặc định là 10
    - Format mới (6 phần tử): (question, options, answer_index, points, explanation, source)
    
    - points: số điểm nếu đúng (mặc định 10 nếu không có).
    - Cấu trúc: (question, options, answer_index, [points], explanation, source)
    """
    result = []
    for i, item in enumerate(data):
        # Xử lý cả 2 format: tuple 5 hoặc 6 phần tử
        if len(item) == 5:
            # Format cũ: (q, opts, ans, explain, source)
            q, opts, ans, explain, source = item
            pts = 10  # Mặc định điểm
        elif len(item) == 6:
            # Format mới: (q, opts, ans, pts, explain, source)
            q, opts, ans, pts, explain, source = item
        else:
            raise ValueError(f"Tuple câu hỏi không hợp lệ tại индекс {i}: kỳ vọng 5 hoặc 6 phần tử, nhận được {len(item)}")
        
        result.append(dict(
            id=f"{prefix}_q{i+1}",
            question=q,
            options=opts,
            answer=ans,  # chỉ số đáp án đúng trong options
            points=pts,  # số điểm nếu đúng
            explanation=explain,  # giải thích sau khi trả lời
            source=source  # nguồn tài liệu
        ))
    return result


PAC_BO = {
    "clues": _clues("pacbo", ["Nguyễn Ái Quốc trở về Tổ quốc", "Hội nghị Trung ương lần thứ tám", "Thành lập Mặt trận Việt Minh", "Chuẩn bị lực lượng giải phóng dân tộc"], ["Ngày 28/01/1941, Nguyễn Ái Quốc trở về nước qua mốc biên giới Cao Bằng.", "Hội nghị Trung ương 8 họp tại Pác Bó từ ngày 10 đến 19/5/1941.", "Hội nghị quyết định thành lập Việt Nam Độc lập Đồng minh (Việt Minh).", "Cao Bằng trở thành căn cứ quan trọng cho phong trào giải phóng dân tộc."], "Lịch sử Việt Nam, tập 8, Viện Sử học"),
    "questions": _questions("pacbo", [
        ("Nguyễn Ái Quốc trở về Tổ quốc vào năm nào?", ["1930", "1941", "1945", "1954"], 1, "Người trở về nước ngày 28/01/1941.", "Lịch sử Việt Nam, tập 8"),
        ("Hội nghị Trung ương 8 họp vào tháng nào?", ["1/1941", "3/1941", "5/1941", "8/1941"], 2, "Hội nghị diễn ra từ ngày 10 đến 19/5/1941.", "Văn kiện Đảng Toàn tập, tập 7"),
        ("Mặt trận được thành lập tại Hội nghị Trung ương 8 có tên gì?", ["Việt Minh", "Mặt trận Liên Việt", "Mặt trận Dân chủ", "Mặt trận Tổ quốc"], 0, "Việt Nam Độc lập Đồng minh (Việt Minh) ra đời năm 1941.", "Văn kiện Đảng Toàn tập, tập 7"),
    ]),
}

BA_DINH = {
    "clues": _clues("badinh", ["Tổng khởi nghĩa giành chính quyền", "Chính phủ lâm thời ra đời", "Tuyên ngôn Độc lập được soạn thảo", "Tuyên bố độc lập tại Ba Đình"], ["Tháng Tám năm 1945, nhân dân cả nước nổi dậy giành chính quyền.", "Ủy ban Dân tộc Giải phóng Việt Nam được cải tổ thành Chính phủ lâm thời.", "Chủ tịch Hồ Chí Minh soạn thảo Tuyên ngôn Độc lập tại Hà Nội.", "Ngày 2/9/1945, Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa."], "Hồ Chí Minh Toàn tập, tập 4"),
    "questions": _questions("badinh", [
        ("Tuyên ngôn Độc lập được đọc ngày nào?", ["19/08/1945", "02/09/1945", "07/05/1954", "19/12/1946"], 1, "Tuyên ngôn được đọc tại Ba Đình ngày 2/9/1945.", "Hồ Chí Minh Toàn tập, tập 4"),
        ("Ai đọc Tuyên ngôn Độc lập?", ["Trường Chinh", "Võ Nguyên Giáp", "Hồ Chí Minh", "Phạm Văn Đồng"], 2, "Chủ tịch Hồ Chí Minh thay mặt Chính phủ lâm thời đọc Tuyên ngôn.", "Hồ Chí Minh Toàn tập, tập 4"),
        ("Tên nước được khai sinh năm 1945 là gì?", ["Việt Nam Dân chủ Cộng hòa", "Cộng hòa Xã hội Chủ nghĩa Việt Nam", "Đại Nam", "Việt Nam Cộng hòa"], 0, "Nước Việt Nam Dân chủ Cộng hòa ra đời ngày 2/9/1945.", "Tuyên ngôn Độc lập, 1945"),
    ]),
}


DIEN_BIEN = {
    "clues": _clues("dienbien", ["Chiến dịch Đông Xuân 1953-1954", "Điện Biên Phủ thành tập đoàn cứ điểm", "Mở màn chiến dịch", "Chiến thắng ngày 7/5/1954"], ["Quân và dân Việt Nam chủ động mở các chiến dịch trong Đông Xuân 1953-1954.", "Pháp xây dựng tập đoàn cứ điểm Điện Biên Phủ nhằm thu hút và tiêu diệt chủ lực ta.", "Chiến dịch Điện Biên Phủ bắt đầu ngày 13/3/1954.", "Tập đoàn cứ điểm bị tiêu diệt ngày 7/5/1954."], "Lịch sử Việt Nam, tập 9, Viện Sử học"),
    "questions": _questions("dienbien", [
        ("Chiến dịch Điện Biên Phủ kết thúc ngày nào?", ["07/05/1954", "20/07/1954", "02/09/1954", "19/12/1954"], 0, "Chiến dịch toàn thắng ngày 7/5/1954.", "Lịch sử Việt Nam, tập 9"),
        ("Chiến dịch Điện Biên Phủ bắt đầu ngày nào?", ["13/03/1954", "07/05/1954", "19/12/1946", "01/09/1954"], 0, "Chiến dịch mở màn ngày 13/3/1954.", "Điện Biên Phủ - Văn kiện và tư liệu"),
        ("Ai là Tổng Tư lệnh chiến dịch?", ["Võ Nguyên Giáp", "Văn Tiến Dũng", "Nguyễn Chí Thanh", "Hoàng Văn Thái"], 0, "Đại tướng Võ Nguyên Giáp là Tổng Tư lệnh chiến dịch.", "Điện Biên Phủ - Văn kiện và tư liệu"),
    ]),
}
DINH_DOC_LAP = {
    "clues": _clues("dinhdoclap", ["Hiệp định Paris được ký kết", "Giải phóng Tây Nguyên và miền Trung", "Chiến dịch Hồ Chí Minh bắt đầu", "Dinh Độc Lập được giải phóng"], ["Hiệp định Paris về chấm dứt chiến tranh được ký ngày 27/1/1973.", "Cuộc Tổng tiến công mùa Xuân 1975 giải phóng Tây Nguyên và các tỉnh miền Trung.", "Chiến dịch Hồ Chí Minh mở màn ngày 26/4/1975.", "Trưa 30/4/1975, quân giải phóng tiến vào Dinh Độc Lập."], "Đại thắng mùa Xuân 1975, NXB Quân đội Nhân dân"),
    "questions": _questions("dinh", [
        ("Chiến dịch Hồ Chí Minh toàn thắng ngày nào?", ["30/04/1975", "01/05/1975", "26/04/1975", "02/09/1975"], 0, "Chiến dịch kết thúc thắng lợi ngày 30/4/1975.", "Đại thắng mùa Xuân 1975"),
        ("Chiến dịch Hồ Chí Minh mở màn ngày nào?", ["26/04/1975", "30/04/1975", "07/05/1954", "27/01/1973"], 0, "Chiến dịch bắt đầu ngày 26/4/1975.", "Đại thắng mùa Xuân 1975"),
        ("Xe tăng nào húc đổ cổng chính Dinh Độc Lập?", ["Xe tăng 390", "Xe tăng 843", "Xe tăng 985", "Xe tăng 280"], 0, "Xe tăng 390 húc đổ cổng chính Dinh Độc Lập.", "Bảo tàng Lịch sử Quân sự Việt Nam"),
    ]),
}

class _TimelineConfigs(dict):
    """Four canonical quests with extra lookup names that do not inflate len()."""
    aliases = {
        "Hang Pác Bó (Cao Bằng)": "Pac Bo",
        "Pác Bó": "Pac Bo",
        "Quảng trường Ba Đình (Hà Nội)": "Ba Dinh",
        "Ba Đình": "Ba Dinh",
        "Lòng chảo Điện Biên Phủ": "Dien Bien Phu",
        "Điện Biên Phủ": "Dien Bien Phu",
        "Dinh Độc Lập (Sài Gòn)": "Dinh Doc Lap",
        "Dinh Độc Lập": "Dinh Doc Lap",
    }

    def _canonical(self, key):
        return self.aliases.get(key, key)

    def __getitem__(self, key):
        return super().__getitem__(self._canonical(key))

    def __contains__(self, key):
        return super().__contains__(self._canonical(key))

    def get(self, key, default=None):
        return super().get(self._canonical(key), default)


TIMELINE_QUEST_CONFIGS = _TimelineConfigs({
    "Pac Bo": PAC_BO,
    "Ba Dinh": BA_DINH,
    "Dien Bien Phu": DIEN_BIEN,
    "Dinh Doc Lap": DINH_DOC_LAP,
})
