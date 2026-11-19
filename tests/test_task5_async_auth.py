"""Hồi quy luồng login async, không dùng mạng hoặc CSDL."""
import asyncio
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from unittest.mock import AsyncMock, Mock
from task5.api_game_data_service import ApiGameDataService
from task5.api_client import ApiClientError
from scenes.login_scene import LoginScene


def test_async_auth_loads_session_and_review_without_sync_transport():
    async def scenario():
        service = ApiGameDataService("http://test")
        service.client.post = Mock(side_effect=AssertionError("HTTP đồng bộ bị cấm"))
        service.browser_client = Mock()
        service.browser_client.request = AsyncMock(side_effect=[
            {"access_token": "test-token", "user": {"ma_nguoi_dung": 1}, "progress": {"score": 30}},
            {"items": [{"id": "q"}]},
        ])
        ok, user, progress = await service.authenticate_async("student", "test-password")
        assert ok and user["ma_nguoi_dung"] == 1 and progress["score"] == 30
        service.async_auth_enabled = True
        assert service.get_review_items() == [{"id": "q"}]
        assert service.load_task4_progress(1) == {}
        service.logout()
        assert service.browser_client.token is None
    asyncio.run(scenario())


def test_async_login_scene_polls_and_avoids_duplicate_submission():
    async def scenario():
        pygame.font.init()
        try:
            service = Mock(async_auth_enabled=True)
            service.authenticate_async = AsyncMock(return_value=(True, {"ma_nguoi_dung": 1}, {"score": 0}))
            scene = LoginScene(service)
            scene.input_login_user.text = "student"
            scene.input_login_pass.text = "test-password"
            assert scene.do_login() is None
            assert scene.do_login() is None
            assert scene.poll_auth_result() is None
            await asyncio.sleep(0)
            result = scene.poll_auth_result()
            assert result["action"] == "login_success"
            service.authenticate_async.assert_awaited_once()
            assert scene.poll_auth_result() is None
        finally:
            pygame.font.quit()
    asyncio.run(scenario())


def test_async_auth_failure_clears_partial_token():
    async def scenario():
        service = ApiGameDataService("http://test")
        service.browser_client = Mock()
        service.browser_client.request = AsyncMock(side_effect=[
            {"access_token": "test-token", "user": {"ma_nguoi_dung": 1}},
            ApiClientError("network failure"),
        ])
        ok, user, message = await service.authenticate_async("student", "test-password")
        assert not ok and user is None and "network failure" in message
        assert service.client.token is None and service.browser_client.token is None
    asyncio.run(scenario())