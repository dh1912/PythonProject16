"""Màn hình Bảng Vàng top 10."""
import pygame
import asyncio
from .font_utils import task5_font


class LeaderboardScene:
    def __init__(self, data_service=None):
        self.data_service = data_service
        self.rows = []
        self.pending = None
        self.message = "Nhấn R để tải lại | ESC để quay lại"
        self.font = task5_font(24)
        self.title_font = task5_font(34, bold=True)

    def refresh(self):
        if getattr(self.data_service, "async_auth_enabled", False):
            if self.pending is None:
                self.message = "Đang tải Bảng Vàng…"
                self.pending = asyncio.create_task(self.data_service.get_leaderboard_async())
            return
        try: self.rows = self.data_service.get_leaderboard(); self.message = ""
        except Exception as exc: self.message = f"Không tải được Bảng Vàng: {exc}"

    def poll_pending(self):
        if self.pending is not None and self.pending.done():
            task, self.pending = self.pending, None
            try:
                self.rows = task.result()
                self.message = ""
            except Exception as exc:
                self.message = f"Không tải được Bảng Vàng: {exc}"

    def draw(self, screen):
        screen.fill((248, 244, 230)); title = self.title_font.render("BẢNG VÀNG - TOP 10", True, (180, 35, 45)); screen.blit(title, title.get_rect(center=(540, 85)))
        for index, row in enumerate(self.rows[:10]):
            text = self.font.render(f"{index+1}. {row.get('display_name','Người chơi')}  —  {row.get('score',0)} điểm", True, (45,40,35)); screen.blit(text, (230, 160+index*43))
        if self.message:
            label = self.font.render(self.message[:100], True, (50,45,40)); screen.blit(label, (100, 620))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: return "map"
            if event.key == pygame.K_r: self.refresh()
        return None