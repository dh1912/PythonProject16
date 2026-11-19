"""Pygame interface for arranging the four evidence cards chronologically."""
import pygame


class TimelineScene:
    def __init__(self, inventory, board):
        self.inventory = inventory
        self.board = board
        self.score = 0
        self.font = pygame.font.SysFont("segoeui,arial", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial", 16)
        self.drag_source = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.board.check()
            return self.board.verified
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.board.reset()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if 100 <= y <= 555:
                index = max(0, min(3, (y - 125) // 105))
                if x < 500:
                    card_ids = list(self.inventory.clues)
                    if index < len(card_ids):
                        self.drag_source = card_ids[index]
                else:
                    self.board.remove(index)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag_source:
            _, y = event.pos
            if 100 <= y <= 555:
                index = max(0, min(3, (y - 125) // 105))
                self.board.place(self.drag_source, index)
            self.drag_source = None
        return None

    def draw(self, screen):
        screen.fill((245, 239, 220))
        screen.blit(self.font.render("SẮP XẾP DÒNG THỜI GIAN LỊCH SỬ", True, (180, 35, 45)), (50, 30))
        screen.blit(self.small_font.render("Kéo thẻ bên trái vào ô bên phải; ENTER để kiểm tra, R để đặt lại", True, (50, 45, 40)), (50, 70))
        clues = list(self.inventory.clues.values())
        for i in range(4):
            y = 120 + i * 112
            pygame.draw.rect(screen, (255, 255, 255), (50, y, 450, 88), border_radius=8)
            if i < len(clues):
                screen.blit(self.small_font.render(clues[i].title[:55], True, (45, 40, 35)), (65, y + 15))
                screen.blit(self.small_font.render(clues[i].detail[:60], True, (100, 90, 80)), (65, y + 45))
            pygame.draw.rect(screen, (255, 255, 255), (550, y, 470, 88), border_radius=8)
            clue = self.inventory.get(self.board.slots[i]) if self.board.slots[i] else None
            label = f"Giai đoạn {i + 1}: {clue.title if clue else 'Thả manh mối vào đây'}"
            screen.blit(self.small_font.render(label[:58], True, (45, 40, 35)), (565, y + 28))
        color = (45, 125, 80) if self.board.verified else (180, 35, 45)
        screen.blit(self.small_font.render(self.board.message or "", True, color), (55, 585))
