"""Standalone Demo Launcher for Task 4: Quest FSM, Evidence Timeline & History Quiz.

Thực thi độc lập bằng lệnh:
    python -m task4.demo_scene
Phù hợp để trình chiếu báo cáo đồ án Task 4 (Slide 9).
"""

import sys
import os
import pygame

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from task4.quest_system import (
    ClueInventory,
    QuestStateMachine,
    DeductionTimelineBoard,
    QuizSystem,
    build_save_json,
)
from task4.timeline_data import TIMELINE_QUEST_CONFIGS
from task4.timeline_scene import TimelineScene


def run_demo():
    pygame.init()
    pygame.font.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Demo Task 4: He thong Quest, Manh ghep & Timeline - Nhom 11")
    clock = pygame.time.Clock()

    config = TIMELINE_QUEST_CONFIGS["Pac Bo"]
    clues = config["clues"]
    questions = config["questions"]

    fsm = QuestStateMachine([c.id for c in clues])
    fsm.start()

    inventory = ClueInventory()
    for c in clues:
        inventory.add(c)
        fsm.collect_clue(c.id)

    board = DeductionTimelineBoard(inventory, fsm)
    timeline_scene = TimelineScene(inventory, board)
    quiz_system = QuizSystem(questions)

    mode = "timeline"
    quiz_index = 0
    feedback_text = "Keo manh moi ben trai tha vao o ben phai. Nhan ENTER de xac thuc!"
    feedback_color = (180, 35, 45)

    font_title = pygame.font.SysFont("segoeui,arial,timesnewroman", 24, bold=True)
    font_body = pygame.font.SysFont("segoeui,arial,timesnewroman", 18)
    font_small = pygame.font.SysFont("segoeui,arial,timesnewroman", 15)

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if mode == "timeline":
                timeline_scene.handle_event(event)
                if board.verified:
                    mode = "quiz"
                    feedback_text = "Timeline dung chuan! Bat dau 3 cau hoi trac nghiem on tap."
                    feedback_color = (45, 125, 80)
            elif mode == "quiz":
                if event.type == pygame.KEYDOWN:
                    if quiz_index < len(questions):
                        if pygame.K_1 <= event.key <= pygame.K_4:
                            ans_idx = event.key - pygame.K_1
                            res = quiz_system.answer(quiz_index, ans_idx)
                            quiz_index += 1
                            feedback_text = ("Chinh xac (+30d)! " if res["correct"] else "Chua chinh xac (0d)! ") + res.get("explanation", "")
                            feedback_color = (45, 125, 80) if res["correct"] else (180, 35, 45)
                            if quiz_index >= len(questions):
                                fsm.mark_quiz_completed()
                                fsm.complete()
                    else:
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                            mode = "completed"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if quiz_index < len(questions):
                        mx, my = event.pos
                        for idx in range(4):
                            r = pygame.Rect(90, 210 + idx * 68, 900, 52)
                            if r.collidepoint(mx, my):
                                res = quiz_system.answer(quiz_index, idx)
                                quiz_index += 1
                                feedback_text = ("Chinh xac (+30d)! " if res["correct"] else "Chua chinh xac (0d)! ") + res.get("explanation", "")
                                feedback_color = (45, 125, 80) if res["correct"] else (180, 35, 45)
                                if quiz_index >= len(questions):
                                    fsm.mark_quiz_completed()
                                    fsm.complete()
                                break
                    else:
                        mode = "completed"
            elif mode == "completed":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RETURN):
                    running = False

        if mode == "timeline":
            timeline_scene.draw(screen)
        elif mode == "quiz":
            screen.fill((245, 239, 220))
            screen.blit(font_title.render("DEMO TASK 4: ON TAP SU LIEU PAC BO 1941", True, (180, 35, 45)), (55, 30))
            screen.blit(font_title.render(f"Diem: {quiz_system.score}/90", True, (45, 125, 80)), (850, 30))
            if quiz_index < len(questions):
                q = questions[quiz_index]
                screen.blit(font_body.render(f"Cau hoi {quiz_index + 1}/3 (Phim 1-4 hoac click chuot):", True, (100, 90, 80)), (60, 95))
                screen.blit(font_body.render(q["question"], True, (45, 40, 35)), (60, 135))
                for idx, opt in enumerate(q["options"]):
                    r = pygame.Rect(90, 210 + idx * 68, 900, 52)
                    pygame.draw.rect(screen, (255, 255, 255), r, border_radius=8)
                    pygame.draw.rect(screen, (210, 205, 195), r, 2, border_radius=8)
                    screen.blit(font_body.render(f"{chr(65 + idx)}. {opt}", True, (45, 40, 35)), (r.x + 20, r.y + 14))
            else:
                screen.blit(font_title.render("HOAN THANH TOAN BO QUEST PAC BO 1941!", True, (45, 125, 80)), (60, 120))
                screen.blit(font_body.render(f"Diem: {quiz_system.score}/90 - FSM State: COMPLETED", True, (45, 40, 35)), (60, 180))
                btn = pygame.Rect(60, 260, 360, 48)
                pygame.draw.rect(screen, (180, 35, 45), btn, border_radius=8)
                txt = font_body.render("Nhan SPACE xem JSON Payload", True, (255, 255, 255))
                screen.blit(txt, txt.get_rect(center=btn.center))
            screen.blit(font_small.render(feedback_text[:110], True, feedback_color), (60, 520))
        elif mode == "completed":
            screen.fill((30, 30, 35))
            screen.blit(font_title.render("TASK 4 EXPORT PAYLOAD (OpenAPI / REST API Standard):", True, (230, 200, 90)), (55, 30))
            payload = build_save_json("pac_bo_1941", fsm, inventory, quiz_system)
            for l_idx, line in enumerate(payload.splitlines()):
                c = (130, 215, 150) if ":" in line else (240, 240, 240)
                screen.blit(font_body.render(line, True, c), (60, 80 + l_idx * 28))
            screen.blit(font_small.render("Nhan ESC hoac ENTER de dong demo.", True, (180, 180, 180)), (60, 650))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    run_demo()
