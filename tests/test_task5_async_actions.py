"""Luồng thao tác browser không được gọi transport đồng bộ."""
import asyncio
from unittest.mock import AsyncMock, Mock
import pygame
from task5.api_game_data_service import ApiGameDataService
from task5.leaderboard_scene import LeaderboardScene
from task5.review_system import ReviewManager, ReviewStatus
from scenes.review_scene import ReviewScene


def test_browser_actions_and_save_use_async_only():
    async def scenario():
        service = ApiGameDataService("http://test")
        service.async_auth_enabled = True
        service.client.request = Mock(side_effect=AssertionError("Không được gọi urllib"))
        service.browser_client = Mock()
        service.browser_client.request = AsyncMock(side_effect=[
            {"total_score": 30, "correct": True},
            {"total_score": 45, "is_correct": True, "points_awarded": 15},
            {"leaderboard": [{"display_name": "Test", "score": 45}]},
            {"success": True}, {"data": {"score":45}},
            {"success": True}, {"data": {"score":45}},
        ])
        assert (await service.submit_answer_async("task4:q", 1, 30))["correct"]
        assert (await service.retry_review_async("task4:q", 1))["total_score"] == 45
        assert len(await service.get_leaderboard_async()) == 1
        assert service.sync_user_progress(1, 1, 1914, 999999, set())[0]
        assert service.sync_task4_progress(1, 1, ["a"], 1)[0]
        await asyncio.gather(*tuple(service.pending_operations))
        await asyncio.sleep(0)
        assert not service.pending_operations
        assert not service.network_errors
        for call in service.browser_client.request.call_args_list:
            if call.args[1] == "/progress/save":
                assert "score" not in call.args[2]
        service.client.request.assert_not_called()
    asyncio.run(scenario())


def test_async_review_and_leaderboard_poll_without_duplicates():
    async def scenario():
        pygame.font.init()
        try:
            manager = ReviewManager(persistent=False)
            q = manager.record_mistake("q", "A", "Question", ["a", "b"], 1, 0)
            retry = AsyncMock(return_value={"is_correct": True, "total_score": 15, "points_awarded": 15})
            scene = ReviewScene(manager, retry_submitter=retry)
            scene._process_answer(q, 1)
            scene._process_answer(q, 1)
            assert q.status == ReviewStatus.PENDING
            await asyncio.sleep(0)
            scene.poll_pending()
            assert q.status == ReviewStatus.MASTERED
            assert scene.scoring_engine.total_score == 15
            retry.assert_awaited_once()
            service = Mock(async_auth_enabled=True)
            service.get_leaderboard_async = AsyncMock(return_value=[{"display_name": "A", "score": 15}])
            board = LeaderboardScene(service)
            board.refresh(); board.refresh()
            await asyncio.sleep(0)
            board.poll_pending()
            assert board.rows[0]["score"] == 15
            service.get_leaderboard_async.assert_awaited_once()
        finally:
            pygame.font.quit()
    asyncio.run(scenario())


def test_background_save_failure_is_reported():
    async def scenario():
        service = ApiGameDataService("http://test")
        service.async_auth_enabled = True
        service.browser_client = Mock()
        service.browser_client.request = AsyncMock(side_effect=RuntimeError("network down"))
        service.sync_user_progress(1, 1, 1914, 0, set())
        await asyncio.gather(*tuple(service.pending_operations), return_exceptions=True)
        await asyncio.sleep(0)
        assert service.network_errors == ["network down"]
        assert service.save_state == 'failed'
    asyncio.run(scenario())


def test_timeout_after_commit_reconciles_without_reposting():
    async def scenario():
        service = ApiGameDataService('http://test')
        service.async_auth_enabled = True
        service.browser_client = Mock()
        service.browser_client.request = AsyncMock(side_effect=[
            RuntimeError('timeout after commit'),
            {'data': {'score': 45, 'current_loc_id': 2, 'completed': ['A']}}])
        service.sync_user_progress(1, 2, 1930, 999, {'A'})
        assert service.save_state == 'queued'
        assert service._progress['current_loc_id'] == 1
        await asyncio.gather(*tuple(service.pending_operations), return_exceptions=True)
        await asyncio.sleep(0)
        assert service.save_state == 'failed'
        assert service._progress['score'] == 45
        assert service._progress['current_loc_id'] == 2
        assert service.browser_client.request.await_count == 2
    asyncio.run(scenario())


def test_response_from_old_session_cannot_change_score():
    async def scenario():
        import pytest
        from task5.api_client import ApiClientError
        service = ApiGameDataService("http://test")
        service.async_auth_enabled = True
        started = asyncio.Event()
        release = asyncio.Event()
        async def request(*args, **kwargs):
            started.set()
            await release.wait()
            return {"total_score": 999, "correct": True}
        service.browser_client = Mock()
        service.browser_client.request = request
        task = asyncio.create_task(service.submit_answer_async("q", 1, 30))
        await started.wait()
        service.logout()
        release.set()
        with pytest.raises(ApiClientError):
            await task
        assert service._progress["score"] == 0
    asyncio.run(scenario())