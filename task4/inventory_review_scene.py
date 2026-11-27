"""Màn hình giả cổ hợp nhất túi đồ manh mối và ôn tập câu sai."""
import os
import pygame

EVIDENCE_ASSETS = {
    1: "clue_01_the_thuy_thu.png", 2: "clue_02_long_yeu_nuoc.png",
    3: "clue_03_chanh_cuong_van_tat.png", 4: "clue_04_trong_lenh_xo_viet.png",
    5: "clue_05_cot_moc_108.png", 6: "clue_06_nghi_quyet_tw8.png",
    7: "clue_07_quan_lenh_so_1.png", 8: "clue_08_ban_thao_tuyen_ngon.png",
    9: "clue_09_chi_thi_pha_tan.png", 10: "clue_10_co_quyet_chien_quyet_thang.png",
}

BG=(235,222,191); PAPER=(247,236,207); LIGHT=(255,249,229)
WOOD=(91,58,38); COPPER=(161,105,59); RED=(139,43,39); DARK=(56,43,32); GREEN=(57,103,70)

class InventoryReviewScene:
    def __init__(self, notebook_scene, review_scene, width=1080, height=720):
        self.notebook=notebook_scene; self.review=review_scene; self.width=width; self.height=height
        self.tab="inventory"
        self.font=pygame.font.SysFont("segoeui,arial,timesnewroman",16)
        self.bold=pygame.font.SysFont("segoeui,arial,timesnewroman",17,bold=True)
        self.title=pygame.font.SysFont("segoeui,arial,timesnewroman",28,bold=True)
        self.left=pygame.Rect(28,138,440,500); self.right=pygame.Rect(488,138,564,500)
        self.inventory_tab=pygame.Rect(38,82,250,38); self.review_tab=pygame.Rect(298,82,250,38)
        self.back_button=pygame.Rect(880,34,150,38); self.save_button=pygame.Rect(650,585,180,38); self.map_button=pygame.Rect(840,585,190,38)

    def _wrap(self,value,width,font=None,limit=20):
        font=font or self.font; lines=[]; current=""
        for word in str(value).split():
            candidate=(current+" "+word).strip()
            if current and font.size(candidate)[0]>width: lines.append(current); current=word
            else: current=candidate
        if current: lines.append(current)
        return lines[:limit]

    def _text(self,screen,value,x,y,width,color=DARK,font=None,limit=20):
        font=font or self.font
        for line in self._wrap(value,width,font,limit):
            screen.blit(font.render(line,True,color),(x,y)); y+=font.get_linesize()+3
        return y

    def _panel(self,screen,rect,caption):
        pygame.draw.rect(screen,WOOD,rect.inflate(8,8),border_radius=14); pygame.draw.rect(screen,PAPER,rect,border_radius=12); pygame.draw.rect(screen,COPPER,rect,2,border_radius=12)
        screen.blit(self.bold.render(caption,True,RED),(rect.x+16,rect.y+14))

    def _button(self,screen,rect,label,selected=False):
        pygame.draw.rect(screen,GREEN if selected else LIGHT,rect,border_radius=7); pygame.draw.rect(screen,COPPER,rect,2,border_radius=7)
        image=self.bold.render(label,True,LIGHT if selected else DARK); screen.blit(image,image.get_rect(center=rect.center))

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_m): return "map"
            if event.key in (pygame.K_TAB,pygame.K_r): self.tab="review" if self.tab=="inventory" else "inventory"
            result=(self.review if self.tab=="review" else self.notebook).handle_event(event)
            return "map" if result=="map" or result=="back" else None
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.back_button.collidepoint(event.pos) or self.map_button.collidepoint(event.pos): return "map"
            if self.inventory_tab.collidepoint(event.pos): self.tab="inventory"; return None
            if self.review_tab.collidepoint(event.pos): self.tab="review"; return None
            if self.tab == "inventory" and self.left.collidepoint(event.pos):
                index = max(0, (event.pos[1] - 195 + self.notebook.scroll) // 70)
                if index < len(self.notebook.clues_list):
                    self.notebook.set_current(index)
                return None
            if self.tab == "review" and self.save_button.collidepoint(event.pos):
                self.review.feedback_message = "Tiến độ ôn tập đã được ghi nhận."
                return None
        result=(self.review if self.tab=="review" else self.notebook).handle_event(event)
        return "map" if result=="map" or result=="back" else None

    def _draw_header(self,screen):
        header=pygame.Rect(28,18,self.width-56,88); pygame.draw.rect(screen,WOOD,header.inflate(8,8),border_radius=14); pygame.draw.rect(screen,PAPER,header,border_radius=12); pygame.draw.rect(screen,COPPER,header,2,border_radius=12)
        screen.blit(self.title.render("TÚI ĐỒ & ÔN TẬP CÂU SAI",True,RED),(48,32)); self._button(screen,self.inventory_tab,"TÚI ĐỒ MANH MỐI",self.tab=="inventory"); self._button(screen,self.review_tab,"ÔN TẬP CÂU SAI",self.tab=="review"); self._button(screen,self.back_button,"QUAY LẠI BẢN ĐỒ")

    def _draw_inventory(self, screen):
        self._panel(screen,self.left,"MANH MỐI ĐÃ THU THẬP"); self._panel(screen,self.right,"CHI TIẾT MANH MỐI & NGUỒN SỬ LIỆU")
        clues=self.notebook.clues_list; selected=self.notebook.get_idx(); old=screen.get_clip(); screen.set_clip(pygame.Rect(48,190,400,420))
        for index,clue in enumerate(clues):
            rect=pygame.Rect(48,195+index*70-self.notebook.scroll,400,62); pygame.draw.rect(screen,(231,211,171) if index==selected else LIGHT,rect,border_radius=7); pygame.draw.rect(screen,COPPER,rect,1,border_radius=7)
            clue_id = clue.get('ma_manh_moi', clue.get('id'))
            image_name = EVIDENCE_ASSETS.get(int(clue_id)) if str(clue_id).isdigit() else None
            image = None
            if image_name:
                path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'evidence', image_name))
                if os.path.isfile(path): image = pygame.image.load(path)
            text_left = 72
            if image is not None:
                image = pygame.transform.smoothscale(image, (110, 48))
                screen.blit(image, image.get_rect(midleft=(58, rect.centery)))
                text_left = 180
            self._text(screen,f"{index+1}. {clue.get('tieu_de_manh_moi','Mảnh ghép')}",text_left,rect.y+21,290,RED if index==selected else DARK,self.bold,1)
        screen.set_clip(old)
        if self.notebook.current_clue:
            clue=self.notebook.current_clue
            try:
                clue_id=int(str(clue.get('ma_manh_moi', clue.get('id',''))).split(':')[-1])
            except (TypeError,ValueError): clue_id=None
            image_name=EVIDENCE_ASSETS.get(clue_id)
            if image_name:
                path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'evidence', image_name))
                if os.path.isfile(path):
                    image=pygame.image.load(path)
                    scale=min(330/image.get_width(),230/image.get_height(),1.0)
                    if scale<1: image=pygame.transform.smoothscale(image,(round(image.get_width()*scale),round(image.get_height()*scale)))
                    screen.blit(image,image.get_rect(topright=(1035,205)))
            self._text(screen,clue.get('tieu_de_manh_moi','Mảnh ghép'),515,455,500,RED,self.title,2); self._text(screen,f"Sự kiện: {clue.get('ten_su_kien') or 'N/A'} | Năm: {clue.get('nam_dien_ra') or 'N/A'}",515,500,500,GREEN,self.bold,2)

    def _draw_review(self, screen):
        self._panel(screen,self.left,"DANH SÁCH CÂU SAI"); self._panel(screen,self.right,"HỌC ÔN TẬP CÂU SAI"); questions=self.review.get_active_questions(); selected=max(0,min(self.review.selected_index,len(questions)-1)) if questions else 0
        for index,question in enumerate(questions):
            rect=pygame.Rect(48,195+index*72-self.review.list_scroll,400,62); pygame.draw.rect(screen,(231,211,171) if index==selected else LIGHT,rect,border_radius=7); pygame.draw.rect(screen,COPPER,rect,1,border_radius=7); self._text(screen,question.location_name,60,rect.y+8,370,DARK,self.bold,2); self._text(screen,question.status.value,60,rect.y+38,370,GREEN if question.status.value=="MASTERED" else RED,self.font,1)
        if questions:
            question=questions[selected]; self._text(screen,f"Câu hỏi: {question.question}",515,195,500,RED,self.bold,4); self._text(screen,"ĐÁP ÁN ĐÚNG",515,300,500,GREEN,self.bold,1); correct=question.options[question.correct_index] if question.options else "Chưa có dữ liệu"; self._text(screen,correct,515,330,500,DARK,self.font,3); self._text(screen,"GIẢI THÍCH",515,395,500,GREEN,self.bold,1); self._text(screen,question.explanation or "Đọc lại nguồn sử liệu.",515,425,500,DARK,self.font,6)
        else: self._text(screen,"Chưa có câu sai cần ôn tập.",515,220,500,DARK,self.font,3)
        self._button(screen,self.save_button,"LƯU TIẾN ĐỘ"); self._button(screen,self.map_button,"QUAY LẠI BẢN ĐỒ")

    def draw(self,screen):
        screen.fill(BG); self._draw_header(screen); self._draw_inventory(screen) if self.tab=="inventory" else self._draw_review(screen)
