"""Phòng ôn tập có vùng cuộn và dùng chung hình chữ nhật để vẽ/bấm."""
import pygame
from task5.review_system import ReviewManager, ReviewStatus
from task5.scoring_system import ScoringEngine
from task5.font_utils import task5_font


class ReviewScene:
    def __init__(self, review_manager=None, scoring_engine=None, retry_submitter=None):
        self.review_manager = review_manager if review_manager is not None else ReviewManager()
        self.scoring_engine = scoring_engine if scoring_engine is not None else ScoringEngine()
        self.retry_submitter = retry_submitter
        self.selected_index = 0
        self.feedback_message = "Chọn câu hỏi để ôn tập. TAB: tổng kết."
        self.feedback_color = (50, 45, 40)
        self.font = task5_font(18)
        self.title_font = task5_font(25, bold=True)
        self.list_scroll = self.detail_scroll = self.detail_height = 0
        self.show_summary = False
        self.list_view = pygame.Rect(20, 105, 330, 500)
        self.detail_view = pygame.Rect(370, 105, 690, 500)
        self.back_button = pygame.Rect(910, 20, 150, 42)
        self.answer_rects = []

    def get_active_questions(self):
        return self.review_manager.get_pending_questions() + self.review_manager.get_mastered_questions()

    def _wrap(self, text: str, width: int):
        """Xuống dòng theo pixel, bao gồm chuỗi không có khoảng trắng."""
        result = []
        for paragraph in str(text).split("\n"):
            line = ""
            for char in paragraph:
                if line and self.font.size(line+char)[0] > width:
                    result.append(line)
                    line = ""
                line += char
            result.append(line)
        return result

    def _select(self, index: int):
        questions = self.get_active_questions()
        self.selected_index = max(0, min(index, len(questions)-1))
        self.detail_scroll = 0
        top = self.selected_index*82
        if top < self.list_scroll:
            self.list_scroll = top
        elif top+76 > self.list_scroll+self.list_view.h:
            self.list_scroll = top+76-self.list_view.h

    def handle_event(self, event):
        questions = self.get_active_questions()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_m):
                return "map"
            if event.key == pygame.K_TAB:
                self.show_summary = not self.show_summary
            if questions and not self.show_summary:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self._select(self.selected_index+(1 if event.key == pygame.K_DOWN else -1))
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    q = questions[min(self.selected_index, len(questions)-1)]
                    choice = event.key-pygame.K_1
                    if choice < len(q.options):
                        self._process_answer(q, choice)
        elif event.type == pygame.MOUSEWHEEL:
            if self.list_view.collidepoint(pygame.mouse.get_pos()):
                self.list_scroll = max(0, min(self.list_scroll-event.y*48, max(0, len(questions)*82-self.list_view.h)))
            else:
                self.detail_scroll = max(0, min(self.detail_scroll-event.y*48, max(0, self.detail_height-self.detail_view.h)))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.collidepoint(event.pos):
                return "map"
            if self.list_view.collidepoint(event.pos) and questions:
                self._select((event.pos[1]-self.list_view.y+self.list_scroll)//82)
            elif self.detail_view.collidepoint(event.pos) and questions and not self.show_summary:
                q = questions[min(self.selected_index, len(questions)-1)]
                for choice, rect in enumerate(self.answer_rects):
                    if rect.collidepoint(event.pos):
                        self._process_answer(q, choice)
                        break
        return None

    def _process_answer(self, question, choice_index: int):
        try:
            if self.retry_submitter:
                result = self.retry_submitter(question.id, choice_index)
                correct = bool(result["is_correct"])
                self.scoring_engine.total_score = int(result["total_score"])
                earned = int(result.get("points_awarded", 0))
                question.user_choice = choice_index
                question.status = ReviewStatus.MASTERED if correct else ReviewStatus.PENDING
                question.reward_awarded |= earned > 0
            else:
                result = self.review_manager.retry_answer(question.id, choice_index)
                correct = result.is_correct
                earned = self.scoring_engine.record_review_reward(question.id) if correct and self.review_manager.claim_reward(question.id) else 0
            self.feedback_message = f"Chính xác! +{earned} điểm." if correct else "Chưa chính xác. Hãy đọc lại nguồn tư liệu."
            self.feedback_color = (45, 125, 80) if correct else (180, 35, 45)
        except Exception as exc:
            self.feedback_message = f"Chưa lưu được kết quả: {exc}"
            self.feedback_color = (180, 35, 45)

    def draw(self, screen):
        screen.fill((245, 239, 220))
        screen.blit(self.title_font.render("PHÒNG ÔN TẬP", True, (180, 35, 45)), (20, 20))
        summary = self.scoring_engine.export_summary()
        screen.blit(self.font.render(f"Điểm: {summary['total_score']} | Hạng {summary['rank']} — {summary['rank_title']}", True, (50,45,40)), (20, 65))
        pygame.draw.rect(screen, (225,215,195), self.back_button, border_radius=6)
        screen.blit(self.font.render("Quay lại", True, (50,45,40)), (930,30))
        questions = self.get_active_questions()
        self.selected_index = max(0, min(self.selected_index, len(questions)-1))
        previous_clip = screen.get_clip()
        screen.set_clip(self.list_view)
        for index, q in enumerate(questions):
            rect = pygame.Rect(20,105+index*82-self.list_scroll,330,76)
            pygame.draw.rect(screen, (235,215,175) if index == self.selected_index else (255,252,245), rect, border_radius=6)
            for row, text in enumerate(self._wrap(q.location_name,314)[:2]):
                screen.blit(self.font.render(text,True,(50,45,40)),(28,rect.y+5+row*22))
            screen.blit(self.font.render(q.status.value,True,(45,125,80) if q.status == ReviewStatus.MASTERED else (180,35,45)),(28,rect.bottom-25))
        screen.set_clip(previous_clip)
        self.answer_rects = []
        pending = len(self.review_manager.get_pending_questions())
        mastered = len(questions)-pending
        if self.show_summary:
            lines = ["TỔNG KẾT ÔN TẬP",f"Tổng số câu đã sai: {len(questions)}",f"Cần củng cố: {pending}",f"Thành thạo: {mastered}",f"Tỉ lệ: {mastered/len(questions)*100 if questions else 0:.1f}%",f"Hạng {summary['rank']} — {summary['rank_title']}"]
        elif questions:
            lines = self._wrap(questions[self.selected_index].question,666)
        else:
            lines = ["Chưa có câu sai. Hãy tiếp tục khám phá lịch sử!"]
        screen.set_clip(self.detail_view)
        y = 105-self.detail_scroll
        for text in lines:
            screen.blit(self.font.render(text,True,(50,45,40)),(382,y))
            y += 25
        if questions and not self.show_summary:
            q = questions[self.selected_index]
            for index, option in enumerate(q.options):
                wrapped = self._wrap(f"{index+1}. {option}",650)
                rect = pygame.Rect(376,y+8,678,len(wrapped)*25+16)
                self.answer_rects.append(rect)
                pygame.draw.rect(screen,(220,240,220) if index == q.correct_index and q.status == ReviewStatus.MASTERED else (255,252,245),rect,border_radius=5)
                for row,text in enumerate(wrapped):
                    screen.blit(self.font.render(text,True,(50,45,40)),(384,rect.y+8+row*25))
                y = rect.bottom+5
            for text in ("NGUỒN TƯ LIỆU",q.source_title,q.source_author,q.source_publisher,q.source_citation,"GIẢI THÍCH",q.explanation):
                for line in self._wrap(text,666):
                    y += 25
                    screen.blit(self.font.render(line,True,(50,45,40)),(382,y))
        self.detail_height = y+self.detail_scroll-105+30
        screen.set_clip(previous_clip)
        for row,text in enumerate(self._wrap(self.feedback_message,1020)[:2]):
            screen.blit(self.font.render(text,True,self.feedback_color),(20,615+row*23))
        screen.blit(self.font.render("Cuộn chuột: xem thêm | 1–4: trả lời | TAB: tổng kết | ESC: bản đồ",True,(120,115,105)),(20,675))