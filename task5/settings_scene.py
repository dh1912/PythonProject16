"""Display settings screen for resolution and window/fullscreen mode."""
import pygame
from .font_utils import task5_font


class DisplaySettingsScene:
    RESOLUTIONS = ((800, 600), (1080, 720), (1280, 720), (1600, 900), (1920, 1080))
    BACKGROUND = (245, 239, 220)
    RED = (180, 35, 45)
    DARK = (50, 45, 40)
    WHITE = (255, 255, 255)
    GREEN = (45, 125, 80)
    BORDER = (210, 205, 195)

    def __init__(self, resolution=(1280, 720), fullscreen=False):
        self.resolution = tuple(resolution)
        if self.resolution not in self.RESOLUTIONS:
            self.resolution = min(self.RESOLUTIONS, key=lambda item: abs(item[0] - resolution[0]) + abs(item[1] - resolution[1]))
        self.fullscreen = bool(fullscreen)
        self.title_font = task5_font(32, bold=True)
        self.font = task5_font(22)
        self.small_font = task5_font(17)
        self.bold_font = task5_font(20, bold=True)
        self.prev_resolution = pygame.Rect(330, 285, 58, 52)
        self.next_resolution = pygame.Rect(692, 285, 58, 52)
        self.window_button = pygame.Rect(330, 390, 190, 58)
        self.fullscreen_button = pygame.Rect(540, 390, 210, 58)
        self.apply_button = pygame.Rect(430, 500, 220, 54)
        self.back_button = pygame.Rect(30, 25, 150, 44)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                direction = -1 if event.key == pygame.K_LEFT else 1
                index = self.RESOLUTIONS.index(self.resolution)
                self.resolution = self.RESOLUTIONS[(index + direction) % len(self.RESOLUTIONS)]
            elif event.key == pygame.K_RETURN:
                return {"action": "apply", "resolution": self.resolution, "fullscreen": self.fullscreen}
            return None

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        if self.back_button.collidepoint(event.pos):
            return "back"
        if self.prev_resolution.collidepoint(event.pos):
            index = self.RESOLUTIONS.index(self.resolution)
            self.resolution = self.RESOLUTIONS[(index - 1) % len(self.RESOLUTIONS)]
        elif self.next_resolution.collidepoint(event.pos):
            index = self.RESOLUTIONS.index(self.resolution)
            self.resolution = self.RESOLUTIONS[(index + 1) % len(self.RESOLUTIONS)]
        elif self.window_button.collidepoint(event.pos):
            self.fullscreen = False
        elif self.fullscreen_button.collidepoint(event.pos):
            self.fullscreen = True
        elif self.apply_button.collidepoint(event.pos):
            return {"action": "apply", "resolution": self.resolution, "fullscreen": self.fullscreen}
        return None

    def draw(self, screen):
        screen.fill(self.BACKGROUND)
        title = self.title_font.render("CÀI ĐẶT HIỂN THỊ", True, self.RED)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 105)))
        subtitle = self.small_font.render("Chọn độ phân giải và kiểu cửa sổ mong muốn", True, self.DARK)
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 145)))

        panel = pygame.Rect(250, 190, 580, 420)
        pygame.draw.rect(screen, self.WHITE, panel, border_radius=14)
        pygame.draw.rect(screen, self.BORDER, panel, 2, border_radius=14)

        label = self.bold_font.render("ĐỘ PHÂN GIẢI", True, self.DARK)
        screen.blit(label, label.get_rect(center=(540, 245)))
        for rect, text in ((self.prev_resolution, "‹"), (self.next_resolution, "›")):
            pygame.draw.rect(screen, self.RED, rect, border_radius=8)
            text_surface = self.title_font.render(text, True, self.WHITE)
            screen.blit(text_surface, text_surface.get_rect(center=rect.center))
        resolution_label = self.font.render(f"{self.resolution[0]} × {self.resolution[1]}", True, self.DARK)
        screen.blit(resolution_label, resolution_label.get_rect(center=(540, 311)))

        mode_label = self.bold_font.render("CHẾ ĐỘ HIỂN THỊ", True, self.DARK)
        screen.blit(mode_label, mode_label.get_rect(center=(540, 360)))
        for rect, text, selected in (
            (self.window_button, "CỬA SỔ", not self.fullscreen),
            (self.fullscreen_button, "TOÀN MÀN HÌNH", self.fullscreen),
        ):
            color = self.GREEN if selected else self.BORDER
            text_color = self.WHITE if selected else self.DARK
            pygame.draw.rect(screen, color, rect, border_radius=9)
            caption = self.bold_font.render(text, True, text_color)
            screen.blit(caption, caption.get_rect(center=rect.center))

        pygame.draw.rect(screen, self.RED, self.apply_button, border_radius=9)
        apply_label = self.bold_font.render("ÁP DỤNG", True, self.WHITE)
        screen.blit(apply_label, apply_label.get_rect(center=self.apply_button.center))
        pygame.draw.rect(screen, self.BORDER, self.back_button, border_radius=8)
        back_label = self.small_font.render("← Quay lại", True, self.DARK)
        screen.blit(back_label, back_label.get_rect(center=self.back_button.center))
        hint = self.small_font.render("Phím mũi tên: đổi độ phân giải  |  ENTER: áp dụng  |  ESC: quay lại", True, self.DARK)
        screen.blit(hint, (20, 660))
