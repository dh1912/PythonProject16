"""Hồi quy điểm nối deduction, dùng Game chưa khởi tạo cửa sổ và scene giả."""
import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock
import pygame
from main import Game
from task5.scoring_system import ScoringEngine
from services.game_data_service import transform_deduction_questions


def game_fixture(api=False, browser=False):
    game = Game.__new__(Game)
    game.current_user = {"ma_nguoi_dung": 1}
    game.task5_server_enabled = api
    game.scene = "deduction"
    game.data_service = Mock(async_auth_enabled=browser)
    game.scoring_engine = ScoringEngine()
    game._sync_score_views = Mock()
    game.notify = Mock()
    game.handle_deduction_result = Mock()
    game.deduction_scene = SimpleNamespace(finished=False, question_index=0,
        questions=[{"id": "42", "answer": 1, "options": ["a", "b"]}],
        choose=Mock(return_value="correct_question"), handle_event=Mock())
    return game


def test_mapping_keeps_question_id_and_source():
    rows = [{"ma_cau_hoi": 42, "ma_su_kien": 9, "dap_an_dung": "B"}]
    events = [{"ma_su_kien": 9, "ma_dia_diem": 1, "nguon_trich_dan": "Nguồn riêng"}]
    q = transform_deduction_questions(events, rows)["Ben Nha Rong"][0]
    assert q["id"] == "42"
    assert q["source_citation"] == "Nguồn riêng"


def test_deduction_api_error_does_not_advance_or_award():
    game = game_fixture(api=True)
    game.data_service.submit_answer.side_effect = RuntimeError("offline")
    game.handle_deduction_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
    game.deduction_scene.choose.assert_not_called()
    assert game.scoring_engine.total_score == 0
    game.notify.assert_called_once()


def test_server_wrong_result_overrides_cached_correct_answer():
    game = game_fixture(api=True)
    game.data_service.submit_answer.return_value = {"correct": False, "total_score": 0, "points_awarded": -10}
    game.handle_deduction_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
    game.deduction_scene.choose.assert_not_called()
    assert game.deduction_scene.last_answer_correct is False


def test_server_correct_result_advances_without_local_score_formula():
    game = game_fixture(api=True)
    game.data_service.submit_answer.return_value = {"correct": True, "total_score": 54, "points_awarded": 54}
    game.handle_deduction_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
    assert game.scoring_engine.total_score == 54
    game.deduction_scene.choose.assert_called_once_with(0)
    assert game.deduction_scene.questions[0]["answer"] == 1
    assert game.deduction_scene.last_answer_choice == 0


def test_browser_repeated_click_sends_one_request_and_does_not_advance():
    async def scenario():
        game = game_fixture(api=True, browser=True)
        game.data_service.submit_answer_async = AsyncMock(return_value={"correct": True, "total_score": 30})
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
        game.handle_deduction_event(event)
        game.handle_deduction_event(event)
        await game._deduction_task
        game.data_service.submit_answer_async.assert_awaited_once()
        game.deduction_scene.choose.assert_not_called()
    asyncio.run(scenario())