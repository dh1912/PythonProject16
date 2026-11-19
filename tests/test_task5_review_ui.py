"""Kiểm tra bố cục và thao tác của phòng ôn tập, không ghi file thật."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from scenes.review_scene import ReviewScene
from task5.review_system import ReviewManager, ReviewStatus


def test_long_review_scroll_click_and_summary():
    pygame.init()
    try:
        manager = ReviewManager(persistent=False)
        for index in range(15):
            manager.record_mistake(str(index), "Địa điểm dài " * 10, "Câu hỏi dài " * 20,
                                   ["Đáp án dài " * 10, "Đúng"], 1, 0, explanation="Giải thích " * 100)
        scene = ReviewScene(manager)
        screen = pygame.Surface((1080, 720))
        scene.draw(screen)
        assert len(scene.answer_rects) == 2
        assert scene.detail_height > scene.detail_view.height
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        for _ in range(13):
            scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
        assert scene.selected_index == 14
        assert scene.list_scroll > 0
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
        assert manager.questions["14"].status == ReviewStatus.MASTERED
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
        assert scene.show_summary
        scene.draw(screen)
        assert not scene.answer_rects
        assert screen.get_clip() == screen.get_rect()
    finally:
        pygame.quit()


def test_empty_scene_and_back_button():
    pygame.init()
    try:
        manager = ReviewManager(persistent=False)
        scene = ReviewScene(manager)
        scene.draw(pygame.Surface((1080, 720)))
        assert not manager.questions
        assert scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=scene.back_button.center)) == "map"
    finally:
        pygame.quit()