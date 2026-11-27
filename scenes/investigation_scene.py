
import os
import pygame

# Tên nhân vật trong bảng nhan_vat -> asset PNG ở assets/characters/nv.
CHARACTER_ASSETS = {
    "Người dân bến cảng": "nv_nguoi_dan_cang_bien.png",
    "Cán bộ liên lạc quốc tế": "nv_can_bo_lien_lac_quoc_te.png",
    "Tự vệ đỏ Nghệ Tĩnh": "nv_tu_ve_do_nghe_tinh.png",
    "Đồng chí dẫn đường người Tày": "nv_dong_chi_nguoi_tay_dan_duong.png",
    "Đại biểu Quốc dân Đại hội": "nv_dai_bieu_quoc_dan_dai_hoi.png",
    "Chiến sĩ Tự vệ Thành Hoàng Diệu": "nv_chien_si_tu_ve_thanh_hoang_dieu.png",
    "Chiến sĩ Trung đoàn Thủ đô": "nv_chien_si_trung_doan_thu_do.png",
    "Đại tướng Võ Nguyên Giáp": "nv_dai_tuong_vo_nguyen_giap.png",
}

LOCATION_ASSETS = {
    1: "loc_01_ben_nha_rong.png", 2: "loc_02_huong_cang.png",
    3: "loc_03_vinh_ben_thuy.png", 4: "loc_04_hang_pac_bo.png",
    5: "loc_05_tan_trao.png", 6: "loc_06_quang_truong_ba_dinh.png",
    7: "loc_07_can_cu_dia_viet_bac.png", 8: "loc_08_long_chao_dien_bien_phu.png",
    9: "loc_09_dinh_doc_lap.png", 10: "loc_10_cau_hien_luong.png",
    11: "loc_11_ha_noi_dien_bien_phu_tren_khong.png",
}

EVIDENCE_ASSETS = {
    1: "clue_01_the_thuy_thu.png",
    2: "clue_02_long_yeu_nuoc.png",
    3: "clue_03_chanh_cuong_van_tat.png",
    4: "clue_04_trong_lenh_xo_viet.png",
    5: "clue_05_cot_moc_108.png",
    6: "clue_06_nghi_quyet_tw8.png",
    7: "clue_07_quan_lenh_so_1.png",
    8: "clue_08_ban_thao_tuyen_ngon.png",
    9: "clue_09_chi_thi_pha_tan.png",
    10: "clue_10_co_quyet_chien_quyet_thang.png",
}

# Bảng màu giả cổ đồng bộ với màn hình bản đồ.
BACKGROUND = (235, 222, 191)
RED = (139, 43, 39)
DARK = (56, 43, 32)
WHITE = (255, 249, 229)
GREEN = (57, 103, 70)
GOLD = (184, 128, 48)
GRAY = (166, 139, 101)
WOOD = (91, 58, 38)
COPPER = (161, 105, 59)
PARCHMENT = (247, 236, 207)

# Khu vực cố định trên canvas logic 1080x720. Hai panel phải không được giao nhau.
EVENT_PANEL_RECT = pygame.Rect(770, 145, 290, 300)
JOURNAL_PANEL_RECT = pygame.Rect(770, 452, 290, 223)


class InvestigationScene:
    def __init__(self, investigation_data=None):
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 21)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.small_bold = pygame.font.SysFont("segoeui,arial,timesnewroman", 16, bold=True)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 28, bold=True)

        self.location = None
        self.message = "Hãy đọc tư liệu và thu thập manh mối lịch sử."
        self.collected_clues = set()
        self.evidence_options = {}
        self.active_evidence_index = None
        self.selected_clue = None
        self.dialogue_pages = []
        self.dialogue_page = 0
        self.character_image = None
        self.character_asset_path = None
        self.location_image = None
        self.location_asset_path = None
        self.evidence_image = None
        self.evidence_asset_path = None
        self.evidence_images = {}

        # Đổ dữ liệu vào: nếu có dữ liệu từ Service/MySQL thì lấy, ngược lại dùng fallback
        if investigation_data:
            self.investigation_data = investigation_data
        else:
            self.investigation_data = {
            "Ben Nha Rong": {
                "event": "Hanh trinh tim duong cuu nuoc",
                "year": "1911",
                "witness": "Nguoi dan cang",
                "dialogue": (
                    "Toi van nho nhung con tau roi ben cang. "
                    "Day la noi gan voi hanh trinh ra di cua "
                    "Nguyen Tat Thanh nam 1911."
                ),
                "clues": [
                    {
                        "id": "ben_1",
                        "name": "Thong tin ve ben cang",
                        "detail": "Ben Nha Rong nam tai Sai Gon."
                    },
                    {
                        "id": "ben_2",
                        "name": "Moc thoi gian 1911",
                        "detail": "Nguyen Tat Thanh roi Viet Nam nam 1911."
                    }
                ]
            },
            "Hong Kong": {
                "event": "Thanh lap Dang Cong san Viet Nam",
                "year": "1930",
                "witness": "Nguoi lien lac",
                "dialogue": (
                    "Nhieu to chuc cong san da duoc hop nhat "
                    "duoi su chu tri cua Nguyen Ai Quoc vao nam 1930."
                ),
                "clues": [
                    {
                        "id": "hk_1",
                        "name": "Moc thoi gian 1930",
                        "detail": "Su kien thanh lap Dang dien ra nam 1930."
                    },
                    {
                        "id": "hk_2",
                        "name": "Vai tro chu tri",
                        "detail": "Nguyen Ai Quoc chu tri hoi nghi hop nhat."
                    }
                ]
            },
            "Vinh - Ben Thuy": {
                "event": "Phong trao cach mang 1930-1931",
                "year": "1930-1931",
                "witness": "Nguoi dan dia phuong",
                "dialogue": (
                    "Vinh va Ben Thuy la mot trong nhung dia ban "
                    "noi bat cua phong trao cach mang 1930-1931."
                ),
                "clues": [
                    {
                        "id": "vinh_1",
                        "name": "Dia ban phong trao",
                        "detail": "Vinh - Ben Thuy gan voi phong trao 1930-1931."
                    }
                ]
            },
            "Pac Bo": {
                "event": "Nguyen Ai Quoc tro ve Viet Nam",
                "year": "1941",
                "witness": "Can bo cach mang",
                "dialogue": (
                    "Pac Bo gan voi su kien Nguyen Ai Quoc tro ve "
                    "Viet Nam dau nam 1941."
                ),
                "clues": [
                    {
                        "id": "pacbo_1",
                        "name": "Moc thoi gian 1941",
                        "detail": "Nguyen Ai Quoc tro ve Viet Nam nam 1941."
                    },
                    {
                        "id": "pacbo_2",
                        "name": "Dia diem Pac Bo",
                        "detail": "Pac Bo thuoc Cao Bang."
                    }
                ]
            },
            "Tan Trao": {
                "event": "Chuan bi Tong khoi nghia",
                "year": "1945",
                "witness": "Can bo Viet Minh",
                "dialogue": (
                    "Tan Trao la dia diem quan trong trong qua trinh "
                    "chuan bi Tong khoi nghia Thang Tam."
                ),
                "clues": [
                    {
                        "id": "tant_1",
                        "name": "Tan Trao",
                        "detail": "Tan Trao gan voi qua trinh chuan bi Tong khoi nghia."
                    }
                ]
            },
            "Ba Dinh": {
                "event": "Doc Tuyen ngon Doc lap",
                "year": "1945",
                "witness": "Nguoi dan Ha Noi",
                "dialogue": (
                    "Ngay 2 thang 9 nam 1945, Chu tich Ho Chi Minh "
                    "doc Tuyen ngon Doc lap tai Quang truong Ba Dinh."
                ),
                "clues": [
                    {
                        "id": "badinh_1",
                        "name": "Ngay 2-9-1945",
                        "detail": "Tuyen ngon Doc lap duoc doc ngay 2-9-1945."
                    }
                ]
            },
            "Viet Bac": {
                "event": "Can cu dia khang chien",
                "year": "1946-1950",
                "witness": "Nguoi dan Viet Bac",
                "dialogue": (
                    "Viet Bac la can cu dia quan trong cua cuoc "
                    "khang chien chong thuc dan Phap."
                ),
                "clues": [
                    {
                        "id": "vietbac_1",
                        "name": "Can cu Viet Bac",
                        "detail": "Viet Bac giu vai tro quan trong trong khang chien."
                    }
                ]
            },
            "Dien Bien Phu": {
                "event": "Chien dich Dien Bien Phu",
                "year": "1954",
                "witness": "Nguoi dan cong hoa tuyen",
                "dialogue": (
                    "Chien dich Dien Bien Phu ket thuc thang loi "
                    "ngay 7 thang 5 nam 1954."
                ),
                "clues": [
                    {
                        "id": "dbp_1",
                        "name": "Ngay 7-5-1954",
                        "detail": "Chien dich Dien Bien Phu ket thuc thang loi ngay 7-5-1954."
                    },
                    {
                        "id": "dbp_2",
                        "name": "Ket qua chien dich",
                        "detail": "Chien thang tao buoc ngoat quan trong trong cuoc khang chien."
                    }
                ]
            }
        }

    def _load_character_image(self, witness):
        filename = CHARACTER_ASSETS.get(str(witness or "").strip())
        self.character_image = None
        self.character_asset_path = None
        if not filename:
            return
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "characters", "nv", filename))
        if not os.path.isfile(path):
            return
        try:
            # Không gọi convert/convert_alpha ở đây: màn hình test headless có thể
            # chưa có display surface. Pygame vẫn render được Surface ảnh gốc.
            self.character_image = pygame.image.load(path)
            self.character_asset_path = path
        except (pygame.error, OSError):
            self.character_image = None

    def _draw_cover_image(self, screen, image, rect):
        """Phủ kín rect bằng ảnh, giữ tỉ lệ và crop phần dư ở giữa."""
        if image is None or image.get_width() <= 0 or image.get_height() <= 0:
            return False
        scale = max(rect.width / image.get_width(), rect.height / image.get_height())
        size = (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale)))
        scaled = pygame.transform.smoothscale(image, size)
        crop_x = max(0, (scaled.get_width() - rect.width) // 2)
        crop_y = max(0, (scaled.get_height() - rect.height) // 2)
        old_clip = screen.get_clip()
        screen.set_clip(rect)
        screen.blit(scaled, (rect.x - crop_x, rect.y - crop_y))
        screen.set_clip(old_clip)
        return True

    def _load_location_image(self, location):
        self.location_image = None
        self.location_asset_path = None
        location_id = int(location.get("id", location.get("ma_dia_diem", 0)) or 0)
        filename = LOCATION_ASSETS.get(location_id)
        if not filename:
            return
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "locations", filename))
        if not os.path.isfile(path):
            return
        try:
            self.location_image = pygame.image.load(path)
            self.location_asset_path = path
        except (pygame.error, OSError):
            self.location_image = None

    def _load_evidence_image(self, clue):
        self.evidence_image = None
        self.evidence_asset_path = None
        if not clue:
            return
        try:
            clue_id = int(str(clue.get("id", "")).split(":")[-1])
        except (TypeError, ValueError):
            return
        filename = EVIDENCE_ASSETS.get(clue_id)
        if not filename:
            return
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "evidence", filename))
        if not os.path.isfile(path):
            return
        try:
            self.evidence_image = pygame.image.load(path)
            self.evidence_asset_path = path
        except (pygame.error, OSError):
            self.evidence_image = None

    def set_location(self, location):
        self.location = location
        self._load_location_image(location)
        self._load_character_image(self.investigation_data.get(location["name"], {}).get("witness"))
        self.message = "Hoàn thành các mục tiêu bên dưới để thu thập manh mối."
        self.event_scroll = 0
        self.journal_scroll = 0
        self.scroll_dragging = None
        self._scrollbar_state = ()
        self.active_evidence_index = None
        self.selected_clue = None
        self.evidence_options = {}
        data = self.investigation_data.get(location["name"], {})
        dialogue = data.get("dialogue", "")
        if isinstance(dialogue, (list, tuple)):
            full_text = " ".join(str(line) for line in dialogue)
        else:
            full_text = str(dialogue)
        lines = self.wrap_text(full_text, max_length=70)
        self.dialogue_pages = [" ".join(lines[i:i + 3]) for i in range(0, len(lines), 3)] or [""]
        self.dialogue_page = 0
        self.event_scroll = 0
        self.journal_scroll = 0
        clues = data.get("clues", [])
        for index, clue in enumerate(clues):
            # Đảm bảo tên clue đúng không bị trùng hoặc quá chung chung
            correct_name = (clue.get("name") or "").strip()
            # Nếu tên clue rỗng hoặc quá ngắn (≤5 ký tự), dùng 40 ký tự đầu của detail
            if len(correct_name) <= 5:
                detail_fallback = (clue.get("detail") or "")[:45].strip()
                correct_name = detail_fallback if detail_fallback else f"Tư liệu #{index + 1}"

            # Use evidence from other locations as plausible distractors.
            distractors = []
            for other_location, other_data in self.investigation_data.items():
                if other_location == location["name"]:
                    continue
                for other_clue in other_data.get("clues", []):
                    candidate = (other_clue.get("name") or "").strip()
                    # Bỏ qua distractor quá ngắn hoặc trùng tên clue đúng
                    if candidate and len(candidate) > 5 and candidate != correct_name and candidate not in distractors:
                        distractors.append(candidate)
                    if len(distractors) == 2:
                        break
                if len(distractors) == 2:
                    break
            # Tên nhiễu dự phòng cụ thể, không tiết lộ đáp án
            backup_distractors = [
                "Bản Hiệp ước Harmand và Patenôtre",
                "Chiếu Cần Vương khắc gỗ tại Tân Sở",
                "Nhật ký hành quân của đội quân viễn chinh",
                "Thư tịch thương mại thời thuộc địa",
            ]
            bi = 0
            while len(distractors) < 2:
                backup = backup_distractors[bi % len(backup_distractors)]
                bi += 1
                if backup != correct_name and backup not in distractors:
                    distractors.append(backup)
            options = [correct_name, *distractors]
            # Stable deterministic shuffle to avoid always placing the correct item first.
            correct_index = (index + len(location.get("name", ""))) % len(options)
            options[0], options[correct_index] = options[correct_index], options[0]
            self.evidence_options[index] = {
                "options": options,
                "correct_index": correct_index,
                "attempts": 0,
                "hint": clue.get("detail", "Đối chiếu tên tư liệu với sự kiện đang điều tra."),
            }

    def export_official_evidence_answers(self):
        """Xuất đáp án challenge để server kiểm tra; không dùng trong UI production.

        Endpoint/dev-test có thể so sánh ID manh mối + lựa chọn với giá trị này.
        Client bình thường chỉ gửi ID/choice; server không chấp nhận correct_index từ payload.
        """
        return {str(index): {"clue_id": self.investigation_data[self.location["name"]]["clues"][index]["id"],
                            "correct_index": int(challenge["correct_index"])}
                for index, challenge in self.evidence_options.items()}

    def quest_objectives(self):
        """Return actionable objectives; each objective rewards one clue."""
        if not self.location:
            return []
        data = self.investigation_data.get(self.location["name"], {})
        return [
            {
                "clue": clue,
                "complete": clue["id"] in self.collected_clues,
                "objective": (
                    "Đã hoàn thành - manh mối đã ghi vào nhật ký"
                    if clue["id"] in self.collected_clues
                    else clue.get("objective", "Đối chiếu tư liệu với lời kể của nhân chứng")
                ),
            }
            for clue in data.get("clues", [])
        ]

    def draw_text(self, screen, text, x, y, font, color=DARK):
        image = font.render(text, True, color)
        screen.blit(image, (x, y))

    def draw_wrapped(self, screen, text, rect, font, color=DARK, line_gap=3, max_lines=None):
        """Render text wrapped by actual pixel width and clipped to its area."""
        words = str(text).split()
        lines = []
        current = ""
        for word in words:
            chunks = []
            chunk = ""
            for char in word:
                if chunk and font.size(chunk + char)[0] > rect.width:
                    chunks.append(chunk)
                    chunk = char
                else:
                    chunk += char
            if chunk:
                chunks.append(chunk)
            for part in chunks:
                candidate = f"{current} {part}".strip()
                if current and font.size(candidate)[0] > rect.width:
                    lines.append(current)
                    current = part
                else:
                    current = candidate
        if current:
            lines.append(current)
        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while last and font.size(last + "…")[0] > rect.width:
                last = last[:-1]
            lines[-1] = last.rstrip() + "…"
        old_clip = screen.get_clip()
        screen.set_clip(rect)
        line_height = font.get_linesize() + line_gap
        for index, line in enumerate(lines):
            screen.blit(font.render(line, True, color), (rect.x, rect.y + index * line_height))
        screen.set_clip(old_clip)
        return len(lines)

    def wrap_text(self, text, max_length=65):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()

            if len(candidate) > max_length:
                if current:
                    lines.append(current)
                current = word
            else:
                current = candidate

        if current:
            lines.append(current)

        return lines

    def is_complete(self, location=None):
        """True neu da thu thap du MANH MOI cua dia diem."""
        location = location or self.location

        if not location:
            return False

        data = self.investigation_data.get(location["name"])

        if not data:
            return False

        return all(c["id"] in self.collected_clues for c in data["clues"])

    def collect(self, index):
        """Thu thập trực tiếp manh mối chính của sự kiện mà không cần qua câu hỏi chọn bằng chứng nhiễu."""
        if not self.location:
            return

        data = self.investigation_data.get(self.location["name"])

        if not data:
            self.message = "Chưa có dữ liệu điều tra cho địa điểm này."
            return

        if not 0 <= index < len(data["clues"]):
            return

        clue = data["clues"][index]
        self.selected_clue = clue
        self._load_evidence_image(clue)
        self.evidence_images[clue["id"]] = self.evidence_image

        if clue["id"] in self.collected_clues:
            self.message = f"Bạn đã thu thập manh mối này rồi: {clue['name']}"
        else:
            self.collected_clues.add(clue["id"])
            self.message = f"Đã thu thập manh mối chính: {clue['name']}"
            if self.is_complete():
                self.message += ". Đã đủ manh mối - nhấn D để suy luận!"

    def choose_evidence(self, option_index):
        if self.active_evidence_index is None or not self.location:
            return False
        index = self.active_evidence_index
        data = self.investigation_data.get(self.location["name"], {})
        clues = data.get("clues", [])
        if not 0 <= index < len(clues):
            return False
        challenge = self.evidence_options.get(index)
        if not challenge or not 0 <= option_index < len(challenge["options"]):
            return False
        challenge["attempts"] += 1
        clue = clues[index]
        if option_index == challenge["correct_index"]:
            self.collected_clues.add(clue["id"])
            self.active_evidence_index = None
            self.message = "Chính xác! Đã ghi vào nhật ký: " + clue["name"]
            if self.is_complete():
                self.message += ". Đã đủ manh mối - nhấn D để suy luận!"
            return True
        hint = challenge["hint"] if challenge["attempts"] >= 2 else "Chưa đúng. Hãy đọc lại lời nhân chứng và đối chiếu sự kiện, thời gian, địa điểm."
        self.message = "Bằng chứng chưa phù hợp. " + hint
        return False

    def _scrollbar(self, screen, track, max_scroll, scroll):
        """Draw a compact scrollbar without covering the text area."""
        pygame.draw.rect(screen, (224, 204, 165), track, border_radius=4)
        if max_scroll <= 0:
            thumb = track.copy()
        else:
            thumb_h = max(24, round(track.height * track.height / (track.height + max_scroll)))
            thumb_y = track.y + round((track.height - thumb_h) * scroll / max_scroll)
            thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_h)
        pygame.draw.rect(screen, COPPER, thumb, border_radius=4)
        pygame.draw.rect(screen, WOOD, thumb, 1, border_radius=4)
        return thumb

    def _scroll_text(self, screen, text, rect, font, color=DARK, scroll=0, line_gap=3):
        """Render all wrapped lines inside a clipped, vertically scrollable area."""
        words = str(text).split()
        lines, current = [], ""
        for word in words:
            chunks, chunk = [], ""
            for char in word:
                if chunk and font.size(chunk + char)[0] > rect.width:
                    chunks.append(chunk)
                    chunk = char
                else:
                    chunk += char
            if chunk:
                chunks.append(chunk)
            for part in chunks:
                candidate = f"{current} {part}".strip()
                if current and font.size(candidate)[0] > rect.width:
                    lines.append(current)
                    current = part
                else:
                    current = candidate
        if current:
            lines.append(current)
        line_height = font.get_linesize() + line_gap
        content_height = max(line_height, len(lines) * line_height)
        max_scroll = max(0, content_height - rect.height)
        scroll = max(0, min(int(scroll), max_scroll))
        old_clip = screen.get_clip()
        screen.set_clip(rect)
        for index, line in enumerate(lines):
            screen.blit(font.render(line, True, color),
                        (rect.x, rect.y + index * line_height - scroll))
        screen.set_clip(old_clip)
        return max_scroll

    def _scroll_from_bar(self, mouse_y, track, max_scroll):
        if max_scroll <= 0:
            return 0
        thumb_h = max(24, round(track.height * track.height / (track.height + max_scroll)))
        ratio = max(0, min(1, (mouse_y - track.y - thumb_h / 2) / max(1, track.height - thumb_h)))
        return round(ratio * max_scroll)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, track, maximum, current in self._scrollbar_state:
                if track.collidepoint(event.pos):
                    self.scroll_dragging = name
                    setattr(self, name, self._scroll_from_bar(event.pos[1], track, maximum))
                    return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scroll_dragging = None
            return
        if event.type == pygame.MOUSEMOTION and self.scroll_dragging:
            for name, track, maximum, current in self._scrollbar_state:
                if name == self.scroll_dragging:
                    setattr(self, name, self._scroll_from_bar(event.pos[1], track, maximum))
                    return
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = getattr(event, "pos", None) or pygame.mouse.get_pos()
            if EVENT_PANEL_RECT.collidepoint(mouse_pos):
                self.event_scroll = max(0, self.event_scroll - event.y * 28)
            elif JOURNAL_PANEL_RECT.collidepoint(mouse_pos):
                self.journal_scroll = max(0, self.journal_scroll - event.y * 28)
            return

        # Ban phim: phim 1-9 thu thap manh moi tuong ung
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                if self.dialogue_page < len(self.dialogue_pages) - 1:
                    self.dialogue_page += 1
                    return
            if self.active_evidence_index is not None:
                if pygame.K_1 <= event.key <= pygame.K_3:
                    self.choose_evidence(event.key - pygame.K_1)
                elif event.key == pygame.K_ESCAPE:
                    self.active_evidence_index = None
                    self.message = "Đã đóng phần đối chiếu tư liệu."
                return
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.collect(event.key - pygame.K_1)
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if not self.location:
            return

        mouse_x, mouse_y = event.pos
        if pygame.Rect(getattr(self, "sw", 1080) - 205, 38, 145, 42).collidepoint(event.pos):
            return "back"
        if pygame.Rect(790, 410, 250, 28).collidepoint(event.pos):
            self.message = "Hãy đọc lời kể và chọn một nhiệm vụ tư liệu bên dưới để điều tra."
            return "observe"
        if self.active_evidence_index is not None:
            for option_index in range(3):
                option_rect = pygame.Rect(355, 275 + option_index * 46, 390, 40)
                if option_rect.collidepoint(event.pos):
                    self.choose_evidence(option_index)
                    return
            if not pygame.Rect(340, 195, 420, 315).collidepoint(event.pos):
                self.active_evidence_index = None
                return
        data = self.investigation_data.get(self.location["name"])

        if not data:
            self.message = "Chưa có dữ liệu điều tra cho địa điểm này."
            return

        objectives = self.quest_objectives()
        row_height = 54
        row_gap = 8
        list_top = 435
        for index in range(len(objectives)):
            button_y = list_top + index * (row_height + row_gap)

            if 80 <= mouse_x <= 720 and button_y <= mouse_y <= button_y + row_height:
                # Click vào một dòng nhật ký luôn mở nội dung chi tiết của manh mối.
                self.selected_clue = objectives[index]["clue"]
                self.collect(index)
                return

    def draw(self, screen):
        screen.fill(BACKGROUND)

        header = pygame.Rect(28, 18, screen.get_width() - 56, 92)
        pygame.draw.rect(screen, WOOD, header.inflate(8, 8), border_radius=14)
        pygame.draw.rect(screen, PARCHMENT, header, border_radius=12)
        pygame.draw.rect(screen, COPPER, header, 2, border_radius=12)
        header_title = self.location.get("display_name", "CUỘC ĐIỀU TRA") if self.location else "CUỘC ĐIỀU TRA"
        self.draw_text(screen, header_title, 52, 34, self.title_font, RED)
        self.draw_text(screen, "CUỘC THOẠI NHÂN CHỨNG · THU THẬP DỮ LIỆU LỊCH SỬ", 54, 74, self.small_font, DARK)
        back_rect = pygame.Rect(screen.get_width() - 205, 38, 145, 42)
        pygame.draw.rect(screen, RED, back_rect, border_radius=8)
        pygame.draw.rect(screen, COPPER, back_rect, 2, border_radius=8)
        self.draw_text(screen, "← BẢN ĐỒ", back_rect.x + 25, back_rect.y + 11, self.small_bold, WHITE)

        if not self.location:
            self.draw_text(
                screen, "Chưa chọn địa điểm.",
                60, 150, self.font
            )
            return

        data = self.investigation_data.get(self.location["name"])

        if not data:
            self.draw_text(
                screen,
                "Chưa có nội dung điều tra cho địa điểm này.",
                60, 190, self.font
            )
            return

        # Khung trái: cảnh địa điểm và cuộc thoại nhân chứng.
        scene_panel = pygame.Rect(50, 145, 700, 250)
        pygame.draw.rect(screen, (106, 78, 52), scene_panel, border_radius=12)
        pygame.draw.rect(screen, (137, 103, 70), scene_panel, width=2, border_radius=12)
        pygame.draw.line(screen, (176, 137, 85), (70, 285), (730, 285), 2)
        # Ảnh địa điểm phủ kín toàn bộ khung cảnh, giữ tỉ lệ và crop phần dư.
        # Phủ kín toàn bộ lòng khung, không để dải nền trống quanh ảnh.
        scene_image_rect = pygame.Rect(52, 147, 696, 246)
        self._draw_cover_image(screen, self.location_image, scene_image_rect)
        # Nhân vật là lớp foreground riêng, đặt trên ảnh cảnh.
        if self.character_image is not None:
            image = self.character_image.copy()
            max_size = (150, 105)
            scale = min(max_size[0] / image.get_width(), max_size[1] / image.get_height(), 1.0)
            if scale < 1.0:
                image = pygame.transform.smoothscale(image, (round(image.get_width() * scale), round(image.get_height() * scale)))
            # Nhân vật nằm bên trái, ngay phía trên hộp thoại nhân chứng.
            image_rect = image.get_rect(midbottom=(175, 282))
            screen.blit(image, image_rect)
        elif self.location_image is None:
            for x, y, color in ((170, 235, (139, 43, 39)), (270, 232, (57, 103, 70))):
                pygame.draw.rect(screen, color, (x, y, 30, 48))
                pygame.draw.rect(screen, (224, 180, 125), (x + 7, y - 18, 16, 18))
                pygame.draw.rect(screen, DARK, (x + 4, y + 10, 22, 8))
        # Cột phải được chia thành hai panel riêng: thông tin sự kiện ở trên,
        # nhật ký ở dưới. Trước đây journal_panel được vẽ đè lên event_panel,
        # làm mất phần tóm tắt, nguồn và nút quan sát.
        event_panel = EVENT_PANEL_RECT.copy()
        pygame.draw.rect(screen, WOOD, event_panel.inflate(6, 6), border_radius=14)
        pygame.draw.rect(screen, PARCHMENT, event_panel, border_radius=12)
        pygame.draw.rect(screen, COPPER, event_panel, 2, border_radius=12)
        self.draw_text(screen, "SỰ KIỆN LỊCH SỬ", 792, 160, self.title_font, RED)
        event_content = pygame.Rect(792, 198, 240, 207)
        event_lines = (
            f"{data['event']}  |  Ngày tháng: {data.get('date') or data.get('year', '')}"
            f"  |  Tóm tắt diễn biến: {data.get('summary') or data.get('dialogue', '')}"
            f"  |  Nguồn trích dẫn: {data.get('source', 'Tư liệu lịch sử trong cơ sở dữ liệu.')}"
        )
        event_max = self._scroll_text(screen, event_lines, event_content, self.small_font,
                                      DARK, self.event_scroll)
        event_track = pygame.Rect(1043, event_content.y, 8, event_content.height)
        self._scrollbar(screen, event_track, event_max, self.event_scroll)
        observe_rect = pygame.Rect(790, 410, 250, 28)
        observe_hover = observe_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (164, 52, 47) if observe_hover else RED, observe_rect, border_radius=7)
        pygame.draw.rect(screen, GOLD if observe_hover else COPPER, observe_rect, 2, border_radius=7)
        self.draw_text(screen, "QUAN SÁT & ĐIỀU TRA", 813, 416, self.small_bold, WHITE)

        # Hộp thoại trích dẫn lời kể trong khung cảnh trái.
        npc_panel = pygame.Rect(70, 305, 660, 78)
        pygame.draw.rect(screen, PARCHMENT, npc_panel, border_radius=10)
        pygame.draw.rect(screen, GOLD, npc_panel, 2, border_radius=10)
        self.draw_text(screen, str(data.get("witness", "Nhân chứng lịch sử")), 92, 316, self.small_bold, GREEN)
        page_text = self.dialogue_pages[self.dialogue_page] if self.dialogue_pages else str(data.get("dialogue", ""))
        self.draw_wrapped(screen, "“" + page_text + "”", pygame.Rect(92, 341, 615, 32), self.small_font, DARK, max_lines=2)
        if self.dialogue_page < len(self.dialogue_pages) - 1:
            self.draw_text(screen, "Space / Enter: đọc tiếp", 530, 365, self.small_font, RED)

        # Quest objectives; each completed objective awards its corresponding clue.
        self.draw_text(
            screen, "NHIỆM VỤ THU THẬP MANH MỐI",
            60, 405, self.font, RED
        )

        objectives = self.quest_objectives()
        row_height = 54
        row_gap = 8
        list_top = 435
        list_bottom = screen.get_height() - 45
        for index, objective in enumerate(objectives):
            clue = objective["clue"]
            button_y = list_top + index * (row_height + row_gap)
            if button_y + row_height > list_bottom:
                continue
            collected = objective["complete"]
            button_rect = pygame.Rect(80, button_y, 640, row_height)
            hovered = button_rect.collidepoint(pygame.mouse.get_pos())
            color = GREEN if collected else ((255, 246, 211) if hovered else WHITE)
            pygame.draw.rect(screen, color, button_rect, border_radius=8)
            pygame.draw.rect(screen, GRAY, button_rect, width=2, border_radius=8)

            title = (
                f"{index + 1}. [ĐÃ GHI] {clue['name']}"
                if collected else f"{index + 1}. [NHIỆM VỤ] Đối chiếu tư liệu: {clue['name']}"
            )
            clue_image = self.evidence_images.get(clue["id"])
            if clue_image is not None:
                image = clue_image.copy()
                scale = min(120 / image.get_width(), 48 / image.get_height(), 1.0)
                if scale < 1.0:
                    image = pygame.transform.smoothscale(image, (round(image.get_width() * scale), round(image.get_height() * scale)))
                screen.blit(image, image.get_rect(midleft=(button_rect.x + 10, button_rect.centery)))
            text_left = button_rect.x + 145 if clue_image is not None else button_rect.x + 15
            text_width = button_rect.right - text_left - 12
            self.draw_wrapped(
                screen, title, pygame.Rect(text_left, button_y + 16, text_width, 24),
                self.small_font, WHITE if collected else DARK, max_lines=1
            )

        if self.active_evidence_index is not None:
            challenge = self.evidence_options[self.active_evidence_index]
            clue = data["clues"][self.active_evidence_index]
            panel = pygame.Rect(340, 195, 420, 315)
            pygame.draw.rect(screen, (255, 252, 245), panel, border_radius=12)
            pygame.draw.rect(screen, GOLD, panel, 2, border_radius=12)
            self.draw_text(screen, "CHỌN BẰNG CHỨNG", 365, 206, self.font, RED)
            self.draw_wrapped(screen, "Tư liệu nào liên quan đến sự kiện đang điều tra?", pygame.Rect(365, 235, 370, 36), self.small_font, max_lines=2)
            for option_index, option in enumerate(challenge["options"]):
                rect = pygame.Rect(355, 275 + option_index * 46, 390, 40)
                pygame.draw.rect(screen, WHITE, rect, border_radius=7)
                pygame.draw.rect(screen, GRAY, rect, 1, border_radius=7)
                self.draw_wrapped(screen, f"{option_index + 1}. {option}", rect.inflate(-16, -6), self.small_font, DARK, max_lines=2)
            self.draw_text(screen, "ESC: đóng | Chọn 1-3", 365, 474, self.small_font)

        # Nhật ký là panel độc lập, không phủ lên phần thông tin sự kiện.
        journal_panel = JOURNAL_PANEL_RECT.copy()
        pygame.draw.rect(screen, WOOD, journal_panel.inflate(6, 6), border_radius=14)
        pygame.draw.rect(screen, PARCHMENT, journal_panel, border_radius=12)
        pygame.draw.rect(screen, COPPER, journal_panel, 2, border_radius=12)

        self.draw_text(
            screen, "NHẬT KÝ",
            795, 458, self.small_bold, RED
        )

        journal_content = pygame.Rect(795, 492, 235, 158)
        if self.selected_clue:
            journal_text = (
                "Manh mối: " + str(self.selected_clue.get("name", "")) + "  " +
                (self.selected_clue.get("detail", "") or "Chưa có nội dung chi tiết.")
            )
        else:
            journal_text = self.message
        journal_max = self._scroll_text(screen, journal_text, journal_content, self.small_font,
                                        RED if self.selected_clue else DARK, self.journal_scroll)
        journal_track = pygame.Rect(1038, journal_content.y, 8, journal_content.height)
        self._scrollbar(screen, journal_track, journal_max, self.journal_scroll)
        self._scrollbar_state = (
            ("event_scroll", pygame.Rect(1043, event_content.y, 8, event_content.height), event_max, self.event_scroll),
            ("journal_scroll", journal_track, journal_max, self.journal_scroll),
        )

        collected_here = sum(
            1 for c in data["clues"] if c["id"] in self.collected_clues
        )

        self.draw_text(
            screen,
            f"Manh mối đã thu thập: {collected_here}/{len(data['clues'])}",
            795, 475, self.small_font, GREEN
        )

        if self.active_evidence_index is not None:
            self.draw_wrapped(
                screen, self.message, pygame.Rect(795, 492, 235, 42),
                self.small_font, RED, max_lines=2
            )

        if self.is_complete():
            self.draw_text(
                screen,
                "Đã đủ manh mối! Nhấn D để suy luận.",
                795, 655, self.small_font, RED
            )
