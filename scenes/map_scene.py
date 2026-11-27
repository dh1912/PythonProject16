import os
import math
import pygame

# Bảng màu giả cổ: giấy da, đồng, gỗ và ánh nến ấm.
BACKGROUND = (235, 222, 191)
RED = (139, 43, 39)
DARK = (56, 43, 32)
WHITE = (255, 249, 229)
GREEN = (57, 103, 70)
GRAY = (166, 139, 101)
BLUE = (76, 91, 112)
GOLD = (184, 128, 48)
SEA = (188, 193, 170)
LAND = (208, 184, 132)
LAND_EDGE = (108, 76, 46)
PARCHMENT = (247, 236, 207)
PARCHMENT_DARK = (224, 204, 165)
WOOD = (91, 58, 38)
COPPER = (161, 105, 59)

# Mau theo trang thai dia diem
COLOR_LOCKED = (140, 140, 140)   # chua mo khoa
COLOR_OPEN = GOLD                # co the kham pha
COLOR_DONE = GREEN               # da hoan thanh

# Bố cục chuẩn HD 1280x720 theo đặc tả màn hình bản đồ.
MAP_RECT = (24, 104, 548, 466)
LEGEND_RECT = pygame.Rect(586, 104, 180, 252)
INFO_RECT = pygame.Rect(780, 104, 476, 466)
TIMELINE_RECT = pygame.Rect(24, 584, 1232, 118)
MAP_CONTENT_RECT = pygame.Rect(48, 120, 500, 432)
# bando.jpg là ảnh dọc 736x1030; giữ đúng tỉ lệ khi fit vào vùng bản đồ.
MAP_IMAGE_SIZE = (736, 1030)
MAP_IMAGE_SCALE = min(MAP_CONTENT_RECT.width / MAP_IMAGE_SIZE[0], MAP_CONTENT_RECT.height / MAP_IMAGE_SIZE[1])
MAP_IMAGE_RECT = pygame.Rect(
    MAP_CONTENT_RECT.centerx - round(MAP_IMAGE_SIZE[0] * MAP_IMAGE_SCALE / 2),
    MAP_CONTENT_RECT.centery - round(MAP_IMAGE_SIZE[1] * MAP_IMAGE_SCALE / 2),
    round(MAP_IMAGE_SIZE[0] * MAP_IMAGE_SCALE),
    round(MAP_IMAGE_SIZE[1] * MAP_IMAGE_SCALE),
)

# Tọa độ gốc trong dữ liệu lịch sử; MapScene ánh xạ tỷ lệ vào toàn bộ bando.jpg.
# Bảng này là fallback cho các bản ghi DB cũ chưa có tọa độ chuẩn.
CANONICAL_LOCATION_COORDS = {
    1: (412.0, 490.0), 2: (525.0, 203.0), 3: (376.0, 286.0),
    4: (391.0, 183.0), 5: (367.0, 201.0), 6: (387.0, 224.0),
    7: (389.0, 207.0), 8: (299.0, 217.0), 9: (415.0, 505.0),
    10: (370.0, 320.0), 11: (387.0, 218.0),
}
# Tọa độ dia_diem là pixel trên ảnh gốc 736x1030, không phải tọa độ canvas.
LABEL_OFFSETS = {
    1: (14, 8), 2: (-142, -4), 3: (14, 8), 4: (-148, -18),
    5: (14, -22), 6: (16, 8), 7: (14, 22), 8: (-150, 8),
    9: (14, 28), 10: (14, 8), 11: (-175, -22),
}

# Duong vien Viet Nam don gian hoa (kinh do, vi do), theo chieu kim dong ho.
# Day la hinh minh hoa chu S, khong phai ban do dia ly chinh xac.
VIETNAM_OUTLINE = [
    (102.15, 22.40), (102.55, 22.75), (103.00, 22.45), (103.90, 22.50),
    (104.40, 22.80), (105.00, 23.20), (105.45, 23.35), (106.00, 22.95),
    (106.70, 22.85), (107.40, 22.00), (108.05, 21.53),
    (107.60, 21.35), (107.00, 20.95), (106.80, 20.70), (106.60, 20.35),
    (106.20, 20.00), (105.90, 19.85), (105.85, 19.30), (105.70, 18.80),
    (106.10, 18.30), (106.50, 17.60), (107.10, 16.90), (107.60, 16.40),
    (108.20, 16.10), (108.90, 15.10), (109.20, 13.80), (109.30, 13.00),
    (109.20, 12.20), (109.00, 11.50), (108.10, 10.90), (107.10, 10.40),
    (106.90, 10.30), (106.60, 9.90), (106.10, 9.50), (105.40, 8.65),
    (104.80, 8.60), (104.80, 9.20), (105.05, 9.90), (104.50, 10.40),
    (105.00, 10.90), (105.80, 11.60), (106.40, 11.70), (106.80, 11.80),
    (107.50, 12.30), (107.55, 13.20), (107.50, 14.40), (107.20, 15.20),
    (107.30, 16.15), (106.70, 16.90), (105.60, 17.90), (105.00, 18.60),
    (104.20, 19.10), (104.00, 19.70), (104.60, 20.30), (104.40, 20.80),
    (103.80, 21.30), (103.10, 21.90), (102.80, 22.30),
]


def project(lon, lat):
    """Đổi kinh/vĩ độ sang tọa độ trong khung bản đồ HD."""
    x = MAP_CONTENT_RECT.x + (float(lon) - 102.0) / 7.6 * MAP_CONTENT_RECT.width
    y = MAP_CONTENT_RECT.y + (23.6 - float(lat)) / 15.2 * MAP_CONTENT_RECT.height
    return int(x), int(y)


def project_source(x, y):
    """Đổi pixel ảnh gốc bando.jpg sang pixel màn hình sau khi fit đồng nhất."""
    return (
        round(MAP_IMAGE_RECT.left + float(x) * MAP_IMAGE_SCALE),
        round(MAP_IMAGE_RECT.top + float(y) * MAP_IMAGE_SCALE),
    )


class MapScene:
    def __init__(self, locations=None, db_status=""):
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 15)
        self.small_bold = pygame.font.SysFont("segoeui,arial,timesnewroman", 15, bold=True)
        self.settings_button = pygame.Rect(1190, 28, 46, 46)
        self.explore_button = pygame.Rect(804, 486, 424, 50)
        self.timeline_years = (1911, 1930, 1941, 1945, 1954, 1975)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 30, bold=True)

        self.selected_year = 1914
        self.selected_location = None
        self.dragging = False

        # main.py se gan tap ten cac dia diem da hoan thanh vao day
        self.completed = set()
        self.quest_manager = None
        self.animation_time = 0.0
        self.message = ""
        self.db_status = db_status
        self.player_name = ""
        self.score = 0

        # Tải bando.jpg và giữ nguyên tỉ lệ gốc của toàn bộ ảnh.
        self.map_img_x, self.map_img_y = MAP_IMAGE_RECT.topleft
        self.map_img_w, self.map_img_h = MAP_IMAGE_RECT.size
        self.map_image = None
        self.map_source_size = MAP_IMAGE_SIZE

        map_path = os.path.join(os.path.dirname(__file__), "..", "bando.jpg")
        if os.path.exists(map_path):
            raw_img = pygame.image.load(map_path)
            self.map_source_size = raw_img.get_size()
            scale = min(MAP_CONTENT_RECT.width / self.map_source_size[0], MAP_CONTENT_RECT.height / self.map_source_size[1])
            self.map_img_w = round(self.map_source_size[0] * scale)
            self.map_img_h = round(self.map_source_size[1] * scale)
            self.map_img_x = MAP_CONTENT_RECT.centerx - self.map_img_w // 2
            self.map_img_y = MAP_CONTENT_RECT.centery - self.map_img_h // 2
            self.map_image = pygame.transform.smoothscale(raw_img, (self.map_img_w, self.map_img_h))

        # Lấy dữ liệu địa điểm trực tiếp từ database (không dùng mock fallback)
        if locations is not None:
            self.locations = locations
        else:
            from services.game_data_service import game_data_service
            self.locations = game_data_service.get_locations_from_db()

        for location in self.locations:
            location_id = int(location.get("id", location.get("ma_dia_diem", 0)) or 0)
            source_xy = CANONICAL_LOCATION_COORDS.get(location_id)
            if source_xy:
                location["x"], location["y"] = project_source(*source_xy)
            elif "toa_do_x" in location and "toa_do_y" in location:
                location["x"], location["y"] = project_source(location["toa_do_x"], location["toa_do_y"])
            elif "x" not in location or "y" not in location:
                location["x"], location["y"] = project(location.get("lon", 105.0), location.get("lat", 21.0))
            location.setdefault("label_offset", LABEL_OFFSETS.get(location_id, (14, 0)))

        self.outline = [project(lon, lat) for lon, lat in VIETNAM_OUTLINE]

    # ------------------------------------------------------------
    # TRANG THAI DIA DIEM
    # ------------------------------------------------------------
    def status(self, location):
        """Tra ve "done", "open" hoac "locked".

        Mot dia diem chi duoc mo khoa khi moi dia diem o cac giai doan
        truoc do (start nho hon) da hoan thanh.
        """
        if self.quest_manager:
            quest_status = self.quest_manager.state(location)
            if quest_status == "completed":
                return "done"
            if quest_status == "locked":
                if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
                    return "open"
                return "locked"
            return "open"

        if location["name"] in self.completed:
            return "done"

        # Nếu đã hoàn thành Ba Đình thì luôn mở khóa Điện Biên Phủ
        if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
            return "open"

        for other in self.locations:
            if other["start"] < location["start"] and other["name"] not in self.completed:
                if location["name"] == "Dien Bien Phu" and "Ba Dinh" in self.completed:
                    continue
                return "locked"

        return "open"

    def in_year(self, location):
        return location["start"] <= self.selected_year <= location["end"]

    # ------------------------------------------------------------
    # VE
    # ------------------------------------------------------------
    def draw_text(self, screen, text, x, y, font, color=DARK):
        image = font.render(text, True, color)
        screen.blit(image, (x, y))

    def draw_label(self, screen, location, bold, occupied=None):
        font = self.small_bold if bold else self.small_font
        label_text = location.get("display_name") or location.get("name", "")
        original_name = label_text.split(" (")[0] if " (" in label_text else label_text
        short_name = original_name
        available_width = 210
        while short_name and font.size(short_name)[0] > available_width:
            short_name = short_name[:-1]
        if short_name != original_name:
            short_name = short_name.rstrip() + "…"
        image = font.render(short_name, True, DARK)
        width, height = image.get_size()

        # Try several nearby positions to prevent dense historical locations
        # from drawing their labels on top of one another.
        preferred_right = location.get("side", "r") == "r"
        label_dx, label_dy = location.get("label_offset", (14, location.get("dy", 0)))
        base_y = location["y"] - height // 2 + label_dy
        offsets = [0, -24, 24, -44, 44, -62, 62, -82, 82, -104, 104, -128, 128]
        candidates = []
        for offset in offsets:
            for right in (preferred_right, not preferred_right):
                x = location["x"] + label_dx if right else location["x"] - abs(label_dx) - width
                y = base_y + offset
                rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
                if rect.left < MAP_RECT[0] + 4 or rect.right > MAP_RECT[0] + MAP_RECT[2] - 4:
                    continue
                if rect.top < MAP_RECT[1] + 4 or rect.bottom > MAP_RECT[1] + MAP_RECT[3] - 4:
                    continue
                if not any(rect.colliderect(other) for other in (occupied or [])):
                    candidates.append((rect, x, y))
                    break
            if candidates:
                break
        if not candidates:
            # Keep label visible even in crowded clusters by placing compactly
            # close to its marker; panel clip prevents screen overflow.
            # Search the panel for the closest non-overlapping slot rather than
            # stacking labels on the dense northern markers.
            slots = []
            for y in range(MAP_RECT[1] + 6, MAP_RECT[1] + MAP_RECT[3] - height - 6, 22):
                for x in range(MAP_RECT[0] + 6, MAP_RECT[0] + MAP_RECT[2] - width - 6, 12):
                    rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
                    if not any(rect.colliderect(other) for other in (occupied or [])):
                        slots.append((abs(y - base_y) + abs(x - location["x"]), rect, x, y))
            if slots:
                _, rect, x, y = min(slots, key=lambda slot: slot[0])
            else:
                x = min(max(location["x"] + 14, MAP_RECT[0] + 4), MAP_RECT[0] + MAP_RECT[2] - width - 12)
                y = min(max(base_y, MAP_RECT[1] + 4), MAP_RECT[1] + MAP_RECT[3] - height - 8)
                rect = pygame.Rect(x - 4, y - 2, width + 8, height + 4)
        else:
            rect, x, y = candidates[0]
        if occupied is not None:
            occupied.append(rect)
        location["label_rect"] = rect

        box = pygame.Surface((width + 8, height + 4), pygame.SRCALPHA)
        box.fill((255, 255, 255, 220))
        pygame.draw.rect(box, (180, 180, 180), box.get_rect(), 1)
        screen.blit(box, (x - 4, y - 2))
        screen.blit(image, (x, y))

    def draw_panel_frame(self, screen, rect, fill=PARCHMENT, border=COPPER, radius=14):
        """Khung giấy da dùng chung cho bản đồ, thông tin và timeline."""
        pygame.draw.rect(screen, WOOD, rect.inflate(8, 8), border_radius=radius + 3)
        pygame.draw.rect(screen, fill, rect, border_radius=radius)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=radius)
        pygame.draw.rect(screen, PARCHMENT_DARK, rect.inflate(-8, -8), width=1, border_radius=max(2, radius - 4))

    def draw_map_panel(self, screen):
        panel = pygame.Rect(MAP_RECT)
        self.draw_panel_frame(screen, panel, fill=(229, 218, 185), border=COPPER, radius=16)
        old_clip = screen.get_clip()

        # Bien
        pygame.draw.rect(screen, SEA, panel, border_radius=15)
        screen.set_clip(panel)

        # Ve ban do thuc te bando.jpg neu co
        if self.map_image:
            screen.blit(self.map_image, (self.map_img_x, self.map_img_y))
            pygame.draw.rect(
                screen, (180, 205, 220),
                (self.map_img_x, self.map_img_y, self.map_img_w, self.map_img_h),
                1
            )
        else:
            # Dat lien Viet Nam du phong (hinh chu S)
            pygame.draw.polygon(screen, LAND, self.outline)
            pygame.draw.polygon(screen, LAND_EDGE, self.outline, 2)

            grey_blue = (90, 120, 150)
            self.draw_text(screen, "BIỂN ĐÔNG", 430, 420, self.small_bold, grey_blue)
            self.draw_text(screen, "Q.đ Hoàng Sa (VN)", 440, 340, self.small_font, grey_blue)
            self.draw_text(screen, "Q.đ Trường Sa (VN)", 440, 520, self.small_font, grey_blue)
            self.draw_text(screen, "LÀO", 232, 345, self.small_font, (120, 130, 140))
            self.draw_text(screen, "CAMPUCHIA", 255, 466, self.small_font, (120, 130, 140))

        # Cac diem dia danh
        for location in self.locations:
            status = self.status(location)
            active = self.in_year(location)

            if status == "done":
                color = COLOR_DONE
            elif status == "open":
                color = COLOR_OPEN
            else:
                color = COLOR_LOCKED

            pulse = (1.0 + math.sin(self.animation_time * 3.2)) * 0.5
            radius = (10 if active else 7) + (int(pulse * 3) if status == "open" else 0)
            position = (location["x"], location["y"])

            if status == "open":
                mouse_pos = pygame.mouse.get_pos()
                hovered = pygame.Rect(position[0] - radius - 6, position[1] - radius - 6, (radius + 6) * 2, (radius + 6) * 2).collidepoint(mouse_pos)
                halo_radius = radius + 7 + int(pulse * 4) + (3 if hovered else 0)
                halo = pygame.Surface((halo_radius * 2 + 2, halo_radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    halo, (*color, max(20, 65 - int(pulse * 30))),
                    (halo_radius + 1, halo_radius + 1), halo_radius, 2
                )
                screen.blit(halo, (position[0] - halo_radius - 1, position[1] - halo_radius - 1))

            pygame.draw.circle(screen, color, position, radius)
            pygame.draw.circle(screen, WHITE, position, radius, 2)

            if status == "done":
                x, y = position
                pygame.draw.lines(
                    screen, WHITE, False,
                    [(x - 4, y), (x - 1, y + 4), (x + 5, y - 4)], 2
                )

            # Danh dau dia diem dang duoc chon
            if location == self.selected_location:
                pygame.draw.circle(screen, BLUE, position, 17, 3)

        # Ve nhan trong khung map, khong cat chu hoac tran vien.
        occupied_labels = []
        for location in sorted(self.locations, key=lambda item: item == self.selected_location):
            self.draw_label(
                screen, location,
                bold=(location == self.selected_location or self.in_year(location)),
                occupied=occupied_labels,
            )

        screen.set_clip(old_clip)
        pygame.draw.rect(screen, COPPER, panel, width=2, border_radius=15)

        self.draw_text(screen, "BẢN ĐỒ HÀNH TRÌNH", MAP_RECT[0] + 18, MAP_RECT[1] + 16, self.small_bold, RED)

    def draw_legend(self, screen):
        # Use the empty right side of the map panel instead of covering labels.
        legend_rect = LEGEND_RECT.copy()
        self.draw_panel_frame(screen, legend_rect, fill=(247, 237, 211), border=COPPER, radius=10)
        x = legend_rect.x + 16
        y = legend_rect.y + 18
        self.draw_text(screen, "Chú giải", x, y, self.small_bold, DARK)

        items = [
            (COLOR_LOCKED, "Chưa mở khóa"),
            (COLOR_OPEN, "Có thể khám phá"),
            (COLOR_DONE, "Đã hoàn thành"),
        ]

        for index, (color, text) in enumerate(items):
            cy = y + 32 + index * 26
            pygame.draw.circle(screen, color, (x + 9, cy), 8)
            pygame.draw.circle(screen, WHITE, (x + 9, cy), 8, 2)
            self.draw_text(screen, text, x + 26, cy - 8, self.small_font)

        done = len(self.completed)
        self.draw_text(screen, f"Tiến độ: {done}/{len(self.locations)}", x, legend_rect.bottom - 28, self.small_bold, GREEN)

    def draw_timeline(self, screen):
        min_year, max_year = 1914, 1975
        slider_x, slider_y, slider_width = 190, 640, 900
        axis_right = slider_x + slider_width

        # Use the same year-to-pixel mapping for the knob and every milestone below.
        selected_year = max(min_year, min(max_year, int(self.selected_year)))
        year_to_x = lambda year: slider_x + round(
            (max(min_year, min(max_year, int(year))) - min_year)
            * slider_width / (max_year - min_year)
        )
        knob_x = year_to_x(selected_year)

        timeline_rect = TIMELINE_RECT.copy()
        self.draw_panel_frame(screen, timeline_rect, fill=PARCHMENT, border=COPPER, radius=12)
        self.draw_text(screen, "DÒNG THỜI GIAN LỊCH SỬ", 48, 595, self.small_bold, RED)
        pygame.draw.line(screen, GRAY, (slider_x, slider_y), (axis_right, slider_y), 8)
        pygame.draw.line(screen, RED, (slider_x, slider_y), (knob_x, slider_y), 8)
        pygame.draw.circle(screen, GOLD, (knob_x, slider_y), 12)
        pygame.draw.circle(screen, WOOD, (knob_x, slider_y), 12, 2)
        # Sáu mốc chính của hành trình, luôn hiển thị và có thể bấm chọn.
        for year in self.timeline_years:
            x = year_to_x(year)
            selected = abs(selected_year - year) <= 2
            color = RED if selected else DARK
            pygame.draw.circle(screen, GOLD if selected else PARCHMENT, (x, slider_y), 8)
            pygame.draw.circle(screen, COPPER, (x, slider_y), 8, 2)
            label = self.small_bold.render(str(year), True, color)
            screen.blit(label, (x - label.get_width() // 2, 655))

        if self.quest_manager:
            states = {"completed": "✓", "available": "●", "investigating": "◉", "quiz": "?", "locked": "○"}
            milestones_by_year = {}
            for item in self.quest_manager.timeline():
                year = int(item["year"])
                milestones_by_year.setdefault(year, []).append(item)

            # Place years at their actual positions and pack them into two clear rows.
            row_right_edges = [slider_x - 1, slider_x - 1]
            label_top = 642
            row_gap = self.small_font.get_linesize() + 1
            for year, items in sorted(milestones_by_year.items()):
                x = year_to_x(year)
                priority = {"completed": 5, "investigating": 4, "quiz": 3, "available": 2, "locked": 1}
                representative = max(items, key=lambda item: priority.get(item["state"], 0))
                state = representative["state"]
                color = GREEN if state == "completed" else RED
                pygame.draw.line(screen, color, (x, 600), (x, 608), 2)
                # Status is conveyed by the milestone tick color; print each year once.
                label = self.small_font.render(str(year), True, color)
                text_x = max(slider_x, min(axis_right - label.get_width(), x - label.get_width() // 2))
                text_right = text_x + label.get_width()
                row = next(
                    (i for i, right_edge in enumerate(row_right_edges)
                     if text_x > right_edge + 6),
                    None,
                )
                if row is None:
                    # Dense dates should not intrude into the bottom keyboard hint.
                    row = min(range(2), key=lambda i: row_right_edges[i])
                    text_x = max(slider_x, min(axis_right - label.get_width(), row_right_edges[row] + 7))
                    text_right = text_x + label.get_width()
                row_right_edges[row] = text_right
                screen.blit(label, (text_x, label_top + row * row_gap))

        current_label = self.font.render(f"Năm đang chọn: {selected_year}", True, RED)
        screen.blit(current_label, (540, 595))

    def wrap(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()

            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def draw_information(self, screen):
        panel_x = INFO_RECT.x
        panel_y = INFO_RECT.y

        info_rect = INFO_RECT.copy()
        self.draw_panel_frame(screen, info_rect, fill=PARCHMENT, border=COPPER, radius=12)

        self.draw_text(
            screen, "THÔNG TIN ĐỊA DANH",
            panel_x + 28, panel_y + 18,
            self.small_bold, RED
        )

        if self.selected_location is None:
            y = panel_y + 85

            for line in self.wrap(
                "Hãy bấm vào một địa điểm trên bản đồ để xem thông tin.",
                self.small_font, 420
            ):
                self.draw_text(screen, line, panel_x + 16, y, self.small_font)
                y += 24

            if self.message:
                y += 10
                for line in self.wrap(self.message, self.small_font, 250):
                    self.draw_text(screen, line, panel_x + 20, y, self.small_font, RED)
                    y += 24
            return

        location = self.selected_location
        status = self.status(location)

        display_name = location.get("display_name") or location.get("name", "")
        name_lines = self.wrap(display_name, self.small_bold, 420)
        name_y = panel_y + 58
        for line in name_lines[:2]:
            self.draw_text(screen, line, panel_x + 28, name_y, self.small_bold, GREEN)
            name_y += 21

        if "event_time" in location and location["event_time"]:
            self.draw_text(
                screen,
                f"Thời gian: {location['event_time']}",
                panel_x + 28, name_y + 2,
                self.small_bold, RED
            )

        self.draw_text(
            screen,
            f"Giai đoạn: {location['start']} - {location['end']}",
            panel_x + 28, name_y + 25,
            self.small_font
        )

        y = name_y + 51

        desc_lines = self.wrap(location.get("description", ""), self.small_font, 420)
        for line in desc_lines[:5]:
            self.draw_text(screen, line, panel_x + 28, y, self.small_font)
            y += 23

        status_text = {
            "done": ("Đã hoàn thành - ENTER: xem lại", COLOR_DONE),
            "open": ("Có thể khám phá - ENTER: điều tra", RED),
            "locked": ("Chưa mở khóa", COLOR_LOCKED),
        }[status]

        # Dòng trạng thái nằm trên nút bấm, hoàn toàn tách biệt không bị che.
        self.draw_text(
            screen, status_text[0],
            panel_x + 28, panel_y + 336,
            self.small_bold, status_text[1]
        )

        # Nút bấm nằm gọn bên dưới dòng trạng thái và trong khung thông tin.
        self.explore_button.topleft = (804, 486)
        hovered = self.explore_button.collidepoint(pygame.mouse.get_pos())
        button_color = GREEN if status != "locked" else GRAY
        if hovered and status != "locked":
            button_color = (75, 132, 88)
        pygame.draw.rect(screen, button_color, self.explore_button, border_radius=8)
        pygame.draw.rect(screen, GOLD if hovered and status != "locked" else COPPER, self.explore_button, 3 if hovered else 2, border_radius=8)
        button_text = self.small_bold.render("DI CHUYỂN & KHÁM PHÁ", True, WHITE)
        screen.blit(button_text, button_text.get_rect(center=self.explore_button.center))

    # ------------------------------------------------------------
    # SU KIEN
    # ------------------------------------------------------------
    def year_from_mouse(self, mouse_x):
        slider_x = 190
        slider_width = 900

        ratio = (mouse_x - slider_x) / slider_width
        ratio = max(0, min(1, ratio))

        return round(1914 + ratio * (1975 - 1914))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.settings_button.collidepoint(event.pos):
                return "settings"
            mouse_x, mouse_y = event.pos

            # Bấm trực tiếp vào một trong sáu mốc chính trên timeline.
            timeline_x = lambda year: 190 + round((max(1914, min(1975, year)) - 1914) * 900 / (1975 - 1914))
            for year in getattr(self, "timeline_years", (1911, 1930, 1941, 1945, 1954, 1975)):
                if pygame.Rect(timeline_x(year) - 24, 620, 48, 45).collidepoint(event.pos):
                    self.selected_year = year
                    self.selected_location = None
                    self.message = f"Đã chọn mốc lịch sử năm {year}."
                    return

            # Bấm vào thanh thời gian để chọn năm liên tục.
            if 190 <= mouse_x <= 1090 and abs(mouse_y - 640) <= 20:
                self.dragging = True
                self.selected_year = self.year_from_mouse(mouse_x)
                self.selected_location = None
                self.message = ""
                return

            if getattr(self, "selected_location", None) and getattr(self, "explore_button", pygame.Rect()).collidepoint(event.pos):
                return "explore"

            # Bam vao dia diem (kiem tra ca cham tron va khung chu ten dia danh)
            # Pin chồng nhau: chọn pin gần click nhất trước, rồi mới xét nhãn.
            pins = [loc for loc in self.locations if
                    (mouse_x-loc['x'])**2+(mouse_y-loc['y'])**2 <= 20**2]
            candidates = sorted(pins, key=lambda loc:
                (mouse_x-loc['x'])**2+(mouse_y-loc['y'])**2) if pins else self.locations
            for location in candidates:
                distance_x = mouse_x - location["x"]
                distance_y = mouse_y - location["y"]
                hit_pin = (distance_x ** 2 + distance_y ** 2 <= 20 ** 2)
                hit_label = bool(location.get("label_rect") and location["label_rect"].collidepoint(mouse_x, mouse_y))

                if hit_pin or hit_label:
                    if self.status(location) == "locked":
                        self.selected_location = None
                        self.message = "Địa điểm chưa mở khóa. Hãy hoàn thành các giai đoạn trước."
                    else:
                        self.selected_location = location
                        self.message = ""

                        # Dua thanh thoi gian ve dung giai doan cua dia diem
                        if not self.in_year(location):
                            self.selected_year = location["start"]
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.selected_year = self.year_from_mouse(event.pos[0])
            self.selected_location = None

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def draw_settings_gear(self, screen):
        """Draw a font-independent gear icon so it renders on every system."""
        cx, cy = self.settings_button.center
        for index in range(8):
            angle = index * 45
            vector = pygame.math.Vector2(1, 0).rotate(angle)
            point = (cx + round(14 * vector.x), cy - round(14 * vector.y))
            pygame.draw.line(screen, GREEN, (cx, cy), point, 4)
        pygame.draw.circle(screen, GREEN, (cx, cy), 12, 4)
        pygame.draw.circle(screen, GREEN, (cx, cy), 4)

    def draw(self, screen, dt=1 / 60):
        self.animation_time += min(max(dt, 0.0), 0.05)
        screen.fill(BACKGROUND)

        header = pygame.Rect(24, 14, 1232, 76)
        self.draw_panel_frame(screen, header, fill=(83, 55, 38), border=GOLD, radius=12)
        title = self.title_font.render("HÀNH TRÌNH LỊCH SỬ VIỆT NAM", True, WHITE)
        screen.blit(title, (42, 22))
        subtitle = self.small_font.render("BẢN ĐỒ KÝ ỨC · 1858 - 1975", True, (235, 211, 157))
        screen.blit(subtitle, (44, 58))

        score_text = self.small_bold.render(f"ĐIỂM TRI THỨC: {self.score}", True, (255, 224, 143))
        screen.blit(score_text, (910, 26))
        progress_text = self.small_bold.render(f"TIẾN ĐỘ: {len(self.completed)}/{len(self.locations)}", True, WHITE)
        screen.blit(progress_text, (910, 52))
        pygame.draw.circle(screen, PARCHMENT, self.settings_button.center, 24)
        pygame.draw.circle(screen, GOLD, self.settings_button.center, 24, 2)
        self.draw_settings_gear(screen)

        self.draw_map_panel(screen)
        self.draw_legend(screen)
        self.draw_information(screen)
        self.draw_timeline(screen)
