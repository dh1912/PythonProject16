import pygame
from typing import Optional

from data.db_queries import execute_select_query

class ClueNotebookScene:
    def __init__(self, sw=1080, sh=720):
        self.sw = sw
        self.sh = sh
        self.COLOR_BG = (248, 244, 230)
        self.COLOR_PAPER = (255, 252, 240)
        self.COLOR_TEXT = (45, 40, 35)
        self.COLOR_ACCENT = (180, 35, 45)
        self.COLOR_BORDER = (215, 205, 180)
        self.COLOR_SECONDARY = (120, 115, 110)
        self.font_title = None
        self.font_meta = None
        self.font_content = None
        self.font_button = None
        self.clues_list = []
        self.current_clue = None
        self.scroll = 0
        self.bookmarked = set()
    
    def load_all_clues(self):
        try:
            sql = "SELECT mm.ma_manh_moi, mm.tieu_de_manh_moi, mm.loai_manh_moi, "
            sql += "mm.noi_dung_chi_tiet, sk.ten_su_kien, sk.nam_dien_ra, "
            sql += "nv.ten_nhan_vat, dd.ten_dia_diem, dd.khu_vuc "
            sql += "FROM manh_moi mm "
            sql += "LEFT JOIN su_kien_lich_su sk ON mm.ma_su_kien = sk.ma_su_kien "
            sql += "LEFT JOIN nhan_vat nv ON mm.ma_nhan_vat = nv.ma_nhan_vat "
            sql += "LEFT JOIN dia_diem dd ON sk.ma_dia_diem = dd.ma_dia_diem "
            sql += "ORDER BY sk.nam_dien_ra, mm.thu_tu_timeline_dung"
            rows, status = execute_select_query(sql)
            if rows is None:
                raise RuntimeError(status)
            self.clues_list = rows
            if self.clues_list:
                self.set_current(0)
        except Exception as e:
            print(f"Error: {e}")
    
    def set_current(self, idx):
        if 0 <= idx < len(self.clues_list):
            self.current_clue = self.clues_list[idx]
            self.scroll = 0
    
    def get_idx(self):
        if not self.current_clue:
            return 0
        try:
            return self.clues_list.index(self.current_clue)
        except:
            return 0
    
    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key in (pygame.K_LEFT, pygame.K_UP):
                idx = self.get_idx()
                if idx > 0:
                    self.set_current(idx - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                idx = self.get_idx()
                if idx < len(self.clues_list) - 1:
                    self.set_current(idx + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            by = self.sh - 60
            if 50 <= x <= 200 and by <= y <= by + 40:
                return 'back'
            if 250 <= x <= 400 and by <= y <= by + 40:
                idx = self.get_idx()
                if idx > 0:
                    self.set_current(idx - 1)
            if self.sw - 400 <= x <= self.sw - 250 and by <= y <= by + 40:
                idx = self.get_idx()
                if idx < len(self.clues_list) - 1:
                    self.set_current(idx + 1)
            if self.sw - 200 <= x <= self.sw - 50 and by <= y <= by + 40:
                return 'bookmark'
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll += event.y * 20
    
    def draw(self, screen):
        if not self.current_clue:
            return
        
        screen.fill(self.COLOR_BG)
        px, py = 40, 40
        pw, ph = self.sw - 80, self.sh - 150
        pr = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(screen, self.COLOR_PAPER, pr, border_radius=10)
        pygame.draw.rect(screen, self.COLOR_BORDER, pr, width=3, border_radius=10)
        
        c = self.current_clue
        title = f"NHAT KY MANH MOI: {c['tieu_de_manh_moi']}"
        if self.font_title:
            screen.blit(self.font_title.render(title, True, self.COLOR_ACCENT), (px+30, py+25))
        
        yo = py + 80
        if self.font_meta:
            for t in [f"SU KIEN: {c['ten_su_kien'] or 'N/A'}", 
                     f"NAM: {c['nam_dien_ra'] or 'N/A'}",
                     f"DIA DIEM: {c['ten_dia_diem'] or 'N/A'}",
                     f"NHAN VAT: {c['ten_nhan_vat'] or 'N/A'}"]:
                screen.blit(self.font_meta.render(t, True, self.COLOR_TEXT), (px+30, yo))
                yo += 30
        
        cy = yo + 20
        cr = pygame.Rect(px+30, cy, pw-60, ph-(cy-py)-50)
        pygame.draw.rect(screen, (255,255,255), cr)
        pygame.draw.rect(screen, self.COLOR_BORDER, cr, width=1)
        
        if self.font_content:
            content = c['noi_dung_chi_tiet'] or "(Khong co noi dung)"
            lines = content.split('. ')
            ty = cr.y + 10 - self.scroll
            for line in lines[:15]:
                if cr.y <= ty <= cr.bottom:
                    screen.blit(self.font_content.render(line+'.', True, self.COLOR_TEXT), (cr.x+10, ty))
                ty += 25
        
        by = self.sh - 60
        self._btn(screen, 50, by, 150, 40, "QUAY LAI")
        idx = self.get_idx()
        self._btn(screen, 250, by, 150, 40, "TRUOC", idx==0)
        
        if self.font_meta:
            pg = f"{idx+1}/{len(self.clues_list)}"
            screen.blit(self.font_meta.render(pg, True, self.COLOR_SECONDARY), 
                       (self.sw//2-30, by+10))
        
        self._btn(screen, self.sw-400, by, 150, 40, "TIEP THEO", idx>=len(self.clues_list)-1)
        self._btn(screen, self.sw-200, by, 150, 40, "DANH DAU")
    
    def _btn(self, screen, x, y, w, h, text, disabled=False):
        if not self.font_button:
            return
        color = (200,195,185) if disabled else (230,220,200)
        bc = (150,140,130) if disabled else self.COLOR_BORDER
        tc = self.COLOR_SECONDARY if disabled else self.COLOR_TEXT
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, color, r, border_radius=8)
        pygame.draw.rect(screen, bc, r, width=2, border_radius=8)
        s = self.font_button.render(text, True, tc)
        sr = s.get_rect(center=r.center)
        screen.blit(s, sr)

        return None
