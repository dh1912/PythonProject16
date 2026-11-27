"""Notebook dùng provider trên web và không tăng tiến độ khi chỉ đọc."""
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pygame

from scenes.investigation_scene import InvestigationScene
from task4.clue_notebook_scene import ClueNotebookScene


def test_investigation_location_asset_is_loaded_by_location_id():
    pygame.init()
    try:
        scene = InvestigationScene(investigation_data={"Test": {"witness": "", "clues": []}})
        scene.set_location({"id": 5, "name": "Test"})
        assert scene.location_asset_path is not None
        assert scene.location_asset_path.endswith("loc_05_tan_trao.png")
    finally:
        pygame.quit()


def test_investigation_character_asset_is_loaded_for_witness():
    pygame.init()
    try:
        data = {
            "Test Location": {
                "event": "Test event",
                "year": "1945",
                "witness": "Người dân bến cảng",
                "dialogue": "Dialogue",
                "clues": [],
            }
        }
        scene = InvestigationScene(investigation_data=data)
        scene.set_location({"name": "Test Location", "display_name": "Test Location"})
        assert scene.character_asset_path is not None
        assert scene.character_asset_path.endswith("nv_nguoi_dan_cang_bien.png")
        screen = pygame.Surface((1080, 720))
        scene.draw(screen)
    finally:
        pygame.quit()


def test_investigation_evidence_asset_is_loaded_for_clue():
    pygame.init()
    try:
        scene = InvestigationScene(investigation_data={"Test": {"witness": "", "clues": [{"id": "5", "name": "Cột mốc", "detail": "D"}]}})
        scene.set_location({"name": "Test"})
        scene.collect(0)
        assert scene.evidence_asset_path is not None
        assert scene.evidence_asset_path.endswith("clue_05_cot_moc_108.png")
    finally:
        pygame.quit()


def test_investigation_character_asset_missing_uses_fallback():

    pygame.init()
    try:
        scene = InvestigationScene(investigation_data={
            "Test Location": {"witness": "Nhân vật không có ảnh", "dialogue": "D", "clues": []}
        })
        scene.set_location({"name": "Test Location"})
        assert scene.character_image is None
        assert scene.character_asset_path is None
    finally:
        pygame.quit()


def test_web_notebook_provider_never_opens_sqlite():

    rows=[{'ma_manh_moi':1,'tieu_de_manh_moi':'A'}]
    with patch.object(sys,'platform','emscripten'), patch('data.db_queries.get_db_connection',side_effect=AssertionError('Cấm truy cập DB')):
        scene=ClueNotebookScene(data_provider=lambda:rows)
        scene.load_all_clues()
        assert scene.current_clue==rows[0]
        assert scene.bookmarked==set()


def test_clicking_investigation_clue_selects_and_shows_detail():
    pygame.init()
    try:
        data = {
            "Test Location": {
                "event": "Test event",
                "year": "1945",
                "witness": "Witness",
                "dialogue": "Dialogue",
                "clues": [{
                    "id": "clue-1",
                    "name": "Tài liệu chiến dịch",
                    "detail": "Nội dung chi tiết để người đọc xem trong nhật ký.",
                }],
            }
        }
        scene = InvestigationScene(investigation_data=data)
        scene.set_location({"name": "Test Location", "display_name": "Test Location"})
        event = SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 445))
        scene.handle_event(event)

        assert scene.selected_clue["id"] == "clue-1"
        assert scene.selected_clue["detail"] == "Nội dung chi tiết để người đọc xem trong nhật ký."
        assert "clue-1" in scene.collected_clues
    finally:
        pygame.quit()


def test_changing_investigation_location_clears_selected_clue():
    scene = InvestigationScene(investigation_data={
        "A": {"clues": [{"id": "a", "name": "A", "detail": "Detail A"}]},
        "B": {"clues": [{"id": "b", "name": "B", "detail": "Detail B"}]},
    })
    scene.selected_clue = {"id": "a"}
    scene.set_location({"name": "B"})
    assert scene.selected_clue is None
