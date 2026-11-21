"""Không mở khóa local trước xác nhận quest; lỗi API không giả thành công."""
import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock
from main import Game
from task5.scoring_system import ScoringEngine


def fixture():
    game=Game.__new__(Game)
    game.task5_server_enabled=True
    game.current_user={'ma_nguoi_dung':1}
    game.completed=set()
    game.scoring_engine=ScoringEngine(20)
    game.data_service=Mock(async_auth_enabled=False)
    game.deduction_scene=SimpleNamespace(finished=True)
    game.save_task4_progress=Mock();game.notify=Mock();game._sync_score_views=Mock()
    return game


def test_rejected_quest_has_no_local_completion():
    g=fixture();g.data_service.complete_quest.side_effect=RuntimeError('missing clues')
    assert g._request_quest_confirmation({'id':1,'name':'A'})
    assert not g.completed and g.scoring_engine.total_score==20
    assert not g.deduction_scene.finished


def test_pending_quest_waits_and_does_not_double_submit():
    async def scenario():
        g=fixture();g.data_service.async_auth_enabled=True
        g.data_service.complete_quest_async=AsyncMock(return_value={'total_score':50})
        loc={'id':1,'name':'A'}
        g._request_quest_confirmation(loc);g._request_quest_confirmation(loc)
        assert not g.completed
        await g._quest_task
        g.data_service.complete_quest_async.assert_awaited_once()
    asyncio.run(scenario())