import os
import math
import pygame

# Mau sac
BACKGROUND = (245, 239, 220)
RED = (180, 35, 45)
DARK = (50, 45, 40)
WHITE = (255, 255, 255)
GREEN = (45, 125, 80)
GRAY = (190, 185, 175)
BLUE = (60, 110, 160)
GOLD = (224, 168, 50)
SEA = (216, 246, 255)
LAND = (234, 214, 170)
LAND_EDGE = (140, 100, 60)

# Mau theo trang thai dia diem
COLOR_LOCKED = (140, 140, 140)   # chua mo khoa
COLOR_OPEN = GOLD                # co the kham pha
COLOR_DONE = GREEN               # da hoan thanh

# Khung ban do tren man hinh (x, y, rong, cao)
MAP_RECT = (40, 145, 700, 430)

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
    """Doi (kinh do, vi do) sang toa do (x, y) tren man hinh."""
    x = 250 + (lon - 102.0) * 24.0
    y = 170 + (23.6 - lat) * 26.0
    return int(x), int(y)


class MapScene:
    def __init__(self, locations=None, db_status=""):
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 15)
        self.small_bold = pygame.font.SysFont("segoeui,arial,timesnewroman", 15, bold=True)
        self.settings_button = pygame.Rect(1010, 34, 46, 46)
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

        # Tai hinh anh ban do thuc te
        self.map_img_x = 240
        self.map_img_y = 147
        self.map_img_w = 304
        self.map_img_h = 426
        self.map_image = None

        map_path = os.path.join(os.path.dirname(__file__), "..", "bando.jpg")
        if os.path.exists(map_path):
            raw_img = pygame.image.load(map_path)
            self.map_image = pygame.transform.smoothscale(raw_img, (self.map_img_w, self.map_img_h))

        # Lấy dữ liệu địa điểm trực tiếp từ database (không dùng mock fallback)
        if locations is not None:
            self.locations = locations
        else:
            from services.game_data_service import game_data_service
            self.locations = game_data_service.get_locations_from_db()

        for location in self.locations:
            if "x" not in location or "y" not in location:
                location["x"], location["y"] = project(location.get("lon", 105.0), location.get("lat", 21.0))

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
        base_y = location["y"] - height // 2 + location.get("dy", 0)
        offsets = [0, -24, 24, -44, 44, -62, 62, -82, 82, -104, 104, -128, 128]
        candidates = []
        for offset in offsets:
            for right in (preferred_right, not preferred_right):
                x = location["x"] + 14 if right else location["x"] - 14 - width
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

    def draw_map_panel(self, screen):
        panel = pygame.Rect(MAP_RECT)
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
                halo_radius = radius + 5 + int(pulse * 3)
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

        # Ve ten sau cung de khong bi cham tron che
        occupied_labels = []
        for location in sorted(self.locations, key=lambda item: item == self.selected_location):
            self.draw_label(
                screen, location,
                bold=(location == self.selected_location or self.in_year(location)),
                occupied=occupied_labels,
            )

        screen.set_clip(old_clip)
        pygame.draw.rect(screen, GREEN, panel, width=3, border_radius=15)

        self.draw_text(screen, "BẢN ĐỒ", 60, 158, self.font, GREEN)

        self.draw_legend(screen)

    def draw_legend(self, screen):
        # Use the empty right side of the map panel instead of covering labels.
        x = 555
        y = 205
        legend_rect = pygame.Rect(x - 12, y - 10, 165, 172)
        pygame.draw.rect(screen, WHITE, legend_rect, border_radius=10)
        pygame.draw.rect(screen, (180, 205, 220), legend_rect, 1, border_radius=10)

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
        self.draw_text(
            screen, f"Tiến độ: {done}/{len(self.locations)}",
            x, y + 125, self.small_bold, GREEN
        )

    def draw_timeline(self, screen):
        min_year, max_year = 1914, 1975
        slider_x, slider_y, slider_width = 280, 605, 560
        axis_right = slider_x + slider_width

        # Use the same year-to-pixel mapping for the knob and every milestone below.
        selected_year = max(min_year, min(max_year, int(self.selected_year)))
        year_to_x = lambda year: slider_x + round(
            (max(min_year, min(max_year, int(year))) - min_year)
            * slider_width / (max_year - min_year)
        )
        knob_x = year_to_x(selected_year)

        pygame.draw.line(screen, GRAY, (slider_x, slider_y), (axis_right, slider_y), 8)
        pygame.draw.line(screen, RED, (slider_x, slider_y), (knob_x, slider_y), 8)
        pygame.draw.circle(screen, RED, (knob_x, slider_y), 12)
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
        screen.blit(current_label, (450, 568))

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
        panel_x = 770
        panel_y = 180

        pygame.draw.rect(
            screen, WHITE,
            (panel_x, panel_y, 290, 350),
            border_radius=12
        )

        pygame.draw.rect(
            screen, GRAY,
            (panel_x, panel_y, 290, 350),
            width=2,
            border_radius=12
        )

        self.draw_text(
            screen, "THÔNG TIN ĐỊA DANH",
            panel_x + 20, panel_y + 18,
            self.small_bold, RED
        )

        if self.selected_location is None:
            y = panel_y + 85

            for line in self.wrap(
                "Hãy bấm vào một địa điểm trên bản đồ để xem thông tin.",
                self.small_font, 250
            ):
                self.draw_text(screen, line, panel_x + 20, y, self.small_font)
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
        name_lines = self.wrap(display_name, self.small_bold, 250)
        name_y = panel_y + 58
        for line in name_lines[:2]:
            self.draw_text(screen, line, panel_x + 20, name_y, self.small_bold, GREEN)
            name_y += 21

        if "event_time" in location and location["event_time"]:
            self.draw_text(
                screen,
                f"Thời gian: {location['event_time']}",
                panel_x + 20, name_y + 2,
                self.small_bold, RED
            )

        self.draw_text(
            screen,
            f"Giai đoạn: {location['start']} - {location['end']}",
            panel_x + 20, name_y + 25,
            self.small_font
        )

        y = name_y + 51

        desc_lines = self.wrap(location.get("description", ""), self.small_font, 250)
        for line in desc_lines[:5]:
            self.draw_text(screen, line, panel_x + 20, y, self.small_font)
            y += 23

        status_text = {
            "done": ("Đã hoàn thành - ENTER: xem lại", COLOR_DONE),
            "open": ("Có thể khám phá - ENTER: điều tra", RED),
            "locked": ("Chưa mở khóa", COLOR_LOCKED),
        }[status]

        self.draw_text(
            screen, status_text[0],
            panel_x + 20, panel_y + 285,
            self.small_bold, status_text[1]
        )

        self.draw_text(
            screen, "D: Suy luận (cần đủ manh mối)",
            panel_x + 20, panel_y + 312,
            self.small_font, DARK
        )

    # ------------------------------------------------------------
    # SU KIEN
    # ------------------------------------------------------------
    def year_from_mouse(self, mouse_x):
        slider_x = 280
        slider_width = 560

        ratio = (mouse_x - slider_x) / slider_width
        ratio = max(0, min(1, ratio))

        return round(1914 + ratio * (1975 - 1914))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.settings_button.collidepoint(event.pos):
                return "settings"
            mouse_x, mouse_y = event.pos

            # Bam vao thanh thoi gian
            if 265 <= mouse_x <= 855 and abs(mouse_y - 605) <= 20:
                self.dragging = True
                self.selected_year = self.year_from_mouse(mouse_x)
                self.selected_location = None
                self.message = ""

            # Bam vao dia diem (kiem tra ca cham tron va khung chu ten dia danh)
            for location in self.locations:
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

        title = self.title_font.render("HÀNH TRÌNH LỊCH SỬ VIỆT NAM (1914 - 1975)", True, RED)

        screen.blit(
            title,
            (screen.get_width() // 2 - title.get_width() // 2, 45)
        )

        pygame.draw.circle(screen, WHITE, self.settings_button.center, 24)
        pygame.draw.circle(screen, GREEN, self.settings_button.center, 24, 2)
        self.draw_settings_gear(screen)

        # Hiển thị trạng thái kết nối Cơ sở dữ liệu (MySQL / Offline Cache)
        if self.db_status:
            status_color = GREEN if "Connected" in self.db_status else (160, 130, 40)
            self.draw_text(screen, f"[{self.db_status}]", 40, 115, self.small_bold, status_color)
        # Hiển thị thông tin người chơi & Điểm số từ bảng tien_do_choi
        if self.player_name:
            player_info_str = f"Người chơi: {self.player_name}  |  Điểm: {self.score}"
            self.draw_text(screen, player_info_str, 720, 115, self.small_bold, BLUE)

        self.draw_map_panel(screen)
        self.draw_information(screen)
        self.draw_timeline(screen)
