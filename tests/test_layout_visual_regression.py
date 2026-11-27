"""Regression checks for the 1080x720 logical layout scaled to HD output."

These checks complement browser screenshots: a screenshot can show a changed
pixel, but it cannot reliably explain whether text was clipped by an overlapping
panel. The tests therefore assert the layout contract and render long content.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from scenes.investigation_scene import (
    EVENT_PANEL_RECT,
    JOURNAL_PANEL_RECT,
    InvestigationScene,
)
from task4.clue_notebook_scene import ClueNotebookScene
from task4.quest_system import Clue, ClueInventory, DeductionTimelineBoard, QuestStateMachine
from task4.timeline_scene import TimelineScene


CANVAS = pygame.Rect(0, 0, 1080, 720)
HD_WINDOW = (1280, 720)


def _scene_with_long_content():
    scene = InvestigationScene({
        "Long Place": {
            "event": "Sự kiện lịch sử rất dài cần được xuống dòng đúng kích thước panel",
            "year": "1945",
            "witness": "Nhân chứng có tên dài",
            "dialogue": "Lời kể dài " * 30,
            "summary": "Tóm tắt diễn biến dài " * 20,
            "source": "Nguồn trích dẫn dài " * 20,
            "clues": [{
                "id": "long-1",
                "name": "Manh mối lịch sử có tiêu đề rất dài",
                "detail": "Nội dung manh mối chi tiết " * 20,
            }],
        }
    })
    scene.set_location({"name": "Long Place", "display_name": "Địa điểm lịch sử rất dài"})
    return scene


def test_uniform_ui_scale_preserves_aspect_ratio_when_window_changes():
    for window in ((1280, 720), (1600, 900), (1920, 1080), (1000, 800)):
        scale = min(window[0] / CANVAS.width, window[1] / CANVAS.height)
        size = (round(CANVAS.width * scale), round(CANVAS.height * scale))
        # Pixel rounding may differ by one pixel at odd window sizes.
        assert abs(size[0] / size[1] - CANVAS.width / CANVAS.height) < 0.002
        assert size[0] <= window[0] and size[1] <= window[1]


def test_investigation_panels_do_not_overlap_or_leave_canvas():
    assert not EVENT_PANEL_RECT.colliderect(JOURNAL_PANEL_RECT)
    assert CANVAS.contains(EVENT_PANEL_RECT)
    assert CANVAS.contains(JOURNAL_PANEL_RECT)


def test_long_investigation_content_renders_without_leaking_clip_or_panels():
    pygame.init()
    try:
        scene = _scene_with_long_content()
        screen = pygame.Surface(CANVAS.size)
        scene.draw(screen)

        # A scene must restore the caller's clip after drawing.
        assert screen.get_clip() == screen.get_rect()
        # UI scale must be uniform: 1080x720 in a 1280x720 window becomes
        # 1080x720, centered, rather than being stretched to 1280x720.
        scale = min(HD_WINDOW[0] / CANVAS.width, HD_WINDOW[1] / CANVAS.height)
        scaled_size = (round(CANVAS.width * scale), round(CANVAS.height * scale))
        assert scaled_size == (1080, 720)
        scaled = pygame.transform.smoothscale(screen, scaled_size)
        assert scaled.get_size() == scaled_size
        # The right column remains two separate visible surfaces after rendering.
        assert EVENT_PANEL_RECT.bottom <= JOURNAL_PANEL_RECT.top
        # The action button stays inside the event panel after the layout change.
        assert pygame.Rect(790, 410, 250, 28).inflate(2, 2).colliderect(EVENT_PANEL_RECT)
        event_track = next(item[1] for item in scene._scrollbar_state if item[0] == "event_scroll")
        scene.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=(event_track.centerx, event_track.bottom)
        ))
        scene.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=(event_track.centerx, event_track.bottom)
        ))
        assert scene.event_scroll >= 0
    finally:
        pygame.quit()


def test_notebook_wheel_reveals_content_beyond_old_15_line_limit():
    pygame.init()
    try:
        scene = ClueNotebookScene(1080, 720)
        scene.font_title = pygame.font.Font(None, 24)
        scene.font_meta = pygame.font.Font(None, 18)
        scene.font_content = pygame.font.Font(None, 18)
        scene.font_button = pygame.font.Font(None, 18)
        scene.clues_list = [{
            "tieu_de_manh_moi": "Tài liệu dài",
            "ten_su_kien": "Sự kiện",
            "nam_dien_ra": "1945",
            "ten_dia_diem": "Hà Nội",
            "ten_nhan_vat": "Nhân chứng",
            "noi_dung_chi_tiet": ". ".join(f"Dòng nội dung {i}" for i in range(40)),
        }]
        scene.set_current(0)
        scene.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, y=-20))
        assert scene.scroll > 0
        screen = pygame.Surface((1080, 720))
        scene.draw(screen)
        assert scene.content_track.height > 0
        scene.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=scene.content_track.center
        ))
        scene.handle_event(pygame.event.Event(
            pygame.MOUSEBUTTONUP, button=1, pos=scene.content_track.center
        ))
    finally:
        pygame.quit()


def test_timeline_scene_three_column_antique_layout_renders_and_dragging_works():
    pygame.init()
    try:
        clues = [Clue(f"c{i}", title, "văn kiện", "Nội dung lịch sử dài để kiểm tra wrap chữ.", "Nguồn", i)
                 for i, title in enumerate(("Cột mốc biên giới 108", "Nghị quyết TW 8", "Việt Minh", "Căn cứ Cao Bằng"))]
        inventory = ClueInventory()
        for clue in clues:
            inventory.add(clue)
        machine = QuestStateMachine([clue.id for clue in clues])
        machine.start()
        board = DeductionTimelineBoard(inventory, machine)
        scene = TimelineScene(inventory, board)
        screen = pygame.Surface((1080, 720))
        scene.draw(screen)
        assert scene.left_panel.right < scene.middle_panel.left < scene.middle_panel.right < scene.right_panel.left
        scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(360, 240)))
        scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(780, 230)))
        assert board.slots[0] == "c0"
    finally:
        pygame.quit()




def test_hd_map_scene_layout_coordinates():
    pygame.init()
    try:
        from scenes.map_scene import MapScene, MAP_RECT, LEGEND_RECT, INFO_RECT, TIMELINE_RECT
        scene = MapScene(locations=[{
            "id": 1, "name": "Ben Nha Rong", "display_name": "Bến Nhà Rồng",
            "lon": 106.7, "lat": 10.77, "start": 1911, "end": 1911,
            "description": "Nơi Nguyễn Tất Thành ra đi tìm đường cứu nước."
        }])
        screen = pygame.Surface((1280, 720))
        scene.draw(screen)
        assert MAP_RECT == (24, 104, 548, 466)
        assert LEGEND_RECT.x == 586 and LEGEND_RECT.y == 104 and LEGEND_RECT.width == 180 and LEGEND_RECT.height == 252
        assert INFO_RECT.x == 780 and INFO_RECT.y == 104 and INFO_RECT.width == 476 and INFO_RECT.height == 466
        assert TIMELINE_RECT.x == 24 and TIMELINE_RECT.y == 584 and TIMELINE_RECT.width == 1232 and TIMELINE_RECT.height == 118
        assert scene.explore_button.x == 804 and scene.explore_button.y == 486 and scene.explore_button.width == 424 and scene.explore_button.height == 50
    finally:
        pygame.quit()


def test_investigation_action_button_uses_new_position():
    pygame.init()
    try:
        scene = _scene_with_long_content()
        assert scene.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 420))
        ) == "observe"
    finally:
        pygame.quit()
