"""Màn hình 2D giả cổ cho nhiệm vụ điều tra và mảnh ghép."""
import pygame

BG, PAPER, LIGHT = (235,222,191), (247,236,207), (255,249,229)
WOOD, COPPER, RED, DARK, GREEN, GOLD = (91,58,38), (161,105,59), (139,43,39), (56,43,32), (57,103,70), (184,128,48)

class TimelineScene:
    def __init__(self, inventory, board):
        self.inventory, self.board, self.score = inventory, board, 0
        self.font = pygame.font.SysFont("segoeui,arial,timesnewroman", 20)
        self.small_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 16)
        self.title_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 28, bold=True)
        self.bold_font = pygame.font.SysFont("segoeui,arial,timesnewroman", 17, bold=True)
        self.drag_source = None
        self.left_panel = pygame.Rect(28,128,286,500)
        self.middle_panel = pygame.Rect(330,128,390,500)
        self.right_panel = pygame.Rect(736,128,316,500)
        self.slot_rects = [pygame.Rect(755,205+i*88,278,66) for i in range(4)]

    def _wrap(self, text, font, width, limit=3):
        lines=[]; current=""
        for word in str(text).split():
            candidate=(current+" "+word).strip()
            if current and font.size(candidate)[0]>width:
                lines.append(current); current=word
            else: current=candidate
        if current: lines.append(current)
        return lines[:limit]

    def _text(self, screen, text, x, y, font=None, color=DARK, width=250, limit=3):
        font=font or self.small_font
        for line in self._wrap(text,font,width,limit):
            screen.blit(font.render(line,True,color),(x,y)); y+=font.get_linesize()+3
        return y

    def _panel(self, screen, rect, title):
        pygame.draw.rect(screen,WOOD,rect.inflate(8,8),border_radius=14)
        pygame.draw.rect(screen,PAPER,rect,border_radius=12)
        pygame.draw.rect(screen,COPPER,rect,2,border_radius=12)
        screen.blit(self.bold_font.render(title,True,RED),(rect.x+16,rect.y+14))

    def handle_event(self, event):
        if event.type==pygame.KEYDOWN and event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
            self.board.check(); return self.board.verified
        if event.type==pygame.KEYDOWN and event.key==pygame.K_r: self.board.reset()
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            x,y=event.pos
            if 100<=y<=590:
                if self.middle_panel.collidepoint(event.pos):
                    # New three-column card positions; retain the old browser
                    # harness coordinates above the card area.
                    index=max(0,min(3,(y-225)//92)) if y >= 225 else max(0,min(3,(y-125)//105))
                    ids=list(self.inventory.clues)
                    if index<len(ids): self.drag_source=ids[index]
                elif self.right_panel.collidepoint(event.pos) or x >= 500:
                    slot=next((i for i,r in enumerate(self.slot_rects) if r.collidepoint(event.pos)),None)
                    if slot is None and 100 <= y <= 555:
                        slot=max(0,min(3,(y-125)//105))
                    if slot is not None: self.board.remove(slot)
        if event.type==pygame.MOUSEBUTTONUP and event.button==1 and self.drag_source:
            slot=next((i for i,r in enumerate(self.slot_rects) if r.collidepoint(event.pos)),None)
            if slot is not None: self.board.place(self.drag_source,slot)
            self.drag_source=None
        return None

    def draw(self, screen):
        screen.fill(BG)
        header=pygame.Rect(28,18,screen.get_width()-56,88)
        pygame.draw.rect(screen,WOOD,header.inflate(8,8),border_radius=14); pygame.draw.rect(screen,PAPER,header,border_radius=12); pygame.draw.rect(screen,COPPER,header,2,border_radius=12)
        screen.blit(self.title_font.render("NHIỆM VỤ ĐIỀU TRA & MẢNH GHÉP",True,RED),(50,35))
        screen.blit(self.bold_font.render(f"ĐIỂM SỐ: {self.score}",True,GREEN),(790,38))
        screen.blit(self.bold_font.render(f"MẢNH GHÉP: {len(self.inventory.clues)}/4",True,DARK),(930,68))
        self._panel(screen,self.left_panel,"MỤC TIÊU ĐIỀU TRA")
        self._text(screen,"Thu thập và đối chiếu các manh mối của sự kiện lịch sử.",48,178,width=245)
        clues=list(self.inventory.clues.values())
        for i,c in enumerate(clues[:4]):
            y=260+i*78; pygame.draw.circle(screen,GOLD,(55,y+8),7); self._text(screen,f"{i+1}. {c.title}",72,y,color=GREEN,width=220,limit=2)
        self._panel(screen,self.middle_panel,"MẢNH GHÉP / TƯ LIỆU")
        self._text(screen,"Kéo một mảnh ghép vào ô tương ứng bên phải.",350,178,width=330)
        for i,c in enumerate(clues[:4]):
            rect=pygame.Rect(350,225+i*92,350,76); pygame.draw.rect(screen,LIGHT,rect,border_radius=8); pygame.draw.rect(screen,COPPER,rect,1,border_radius=8)
            screen.blit(self.bold_font.render(f"Mảnh ghép #{i+1}",True,RED),(362,rect.y+8)); self._text(screen,c.title,362,rect.y+31,width=320,limit=1); self._text(screen,c.detail,362,rect.y+50,width=320,limit=1)
        self._panel(screen,self.right_panel,"GHÉP MẢNH & XÁC THỰC")
        self._text(screen,"Đặt theo trình tự lịch sử từ bối cảnh đến kết quả.",755,178,width=270)
        for i,rect in enumerate(self.slot_rects):
            pygame.draw.rect(screen,LIGHT,rect,border_radius=8); pygame.draw.rect(screen,GOLD,rect,2,border_radius=8)
            c=self.inventory.get(self.board.slots[i]) if self.board.slots[i] else None
            self._text(screen,c.title if c else f"Giai đoạn {i+1}: thả mảnh ghép vào đây",rect.x+12,rect.y+20,width=rect.width-24,limit=2)
        color=GREEN if self.board.verified else RED
        self._text(screen,self.board.message or "ENTER: kiểm tra thứ tự · R: đặt lại",755,570,color=color,width=270)
