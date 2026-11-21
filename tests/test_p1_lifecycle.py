"""Không vô hiệu hóa transport: kiểm trạng thái service bằng coroutine có điều khiển."""
import asyncio
from unittest.mock import AsyncMock, Mock
import pytest
from task5.api_game_data_service import ApiGameDataService
from task5.api_client import ApiClientError


def test_expiry_opens_new_session_without_resubmitting():
    async def run():
        service=ApiGameDataService('http://test');service.async_auth_enabled=True
        service.browser_client=Mock()
        service._question_sessions['1']='expired'
        service.browser_client.request=AsyncMock(side_effect=[
            ApiClientError('HTTP 400: Phiên câu hỏi đã hết hạn'),
            {'session_id':'renewed','remaining_seconds':3600}])
        with pytest.raises(ApiClientError,match='hết hạn'):
            await service.submit_answer_async('1',0,1)
        await asyncio.gather(*tuple(service.pending_operations))
        assert service._question_sessions['1']=='renewed'
        assert [c.args[1] for c in service.browser_client.request.call_args_list]==['/quiz/submit','/quiz/start']
    asyncio.run(run())


def test_hud_service_pending_reconciling_failed():
    async def run():
        service=ApiGameDataService('http://test');service.async_auth_enabled=True
        service.browser_client=Mock()
        post=asyncio.Event();read=asyncio.Event()
        async def request(method,path,*args):
            if method=='POST':
                await post.wait();raise ApiClientError('timeout')
            await read.wait();return {'data':{'score':30}}
        service.browser_client.request=request
        service.sync_user_progress(1,1,1914,0,set())
        assert service.save_state=='queued'
        await asyncio.sleep(0);assert service.save_state=='pending'
        post.set();await asyncio.sleep(0);assert service.save_state=='reconciling'
        read.set();await asyncio.gather(*tuple(service.pending_operations),return_exceptions=True)
        assert service.save_state=='failed' and service._progress['score']==30
    asyncio.run(run())


def test_old_queued_write_never_uses_new_token():
    async def run():
        service=ApiGameDataService('http://test');service.async_auth_enabled=True
        service.browser_client=Mock(request=AsyncMock(return_value={}))
        service._write_lock=asyncio.Lock()
        await service._write_lock.acquire()
        task=asyncio.create_task(service.request_async('POST','/progress/save',{}))
        await asyncio.sleep(0)
        service.logout()
        service.browser_client.token='new-account-token'
        service._write_lock.release()
        with pytest.raises(ApiClientError,match='thay đổi'):await task
        service.browser_client.request.assert_not_called()
    asyncio.run(run())