"""Hồi quy response muộn: transport có thể đã commit trước khi logout."""
import asyncio

import pytest

from task5.api_client import ApiClientError
from task5.api_game_data_service import ApiGameDataService


@pytest.mark.parametrize('method,path', [
    ('POST', '/quiz/submit'), ('POST', '/clues/collect'),
    ('POST', '/progress/save'), ('POST', '/quest/complete'),
    ('POST', '/review/retry'), ('GET', '/progress/me'),
    ('GET', '/review/me'),
])
def test_late_transport_response_rejected_after_account_change(method, path):
    async def run():
        service = ApiGameDataService('http://unused')
        entered, release = asyncio.Event(), asyncio.Event()

        class Transport:
            token = 'account-a'

            async def request(self, *args):
                entered.set()
                await release.wait()
                return {'total_score': 999, 'data': {'score': 999}}

        service.browser_client = Transport()
        task = asyncio.create_task(service.request_async(method, path, {}))
        await entered.wait()
        service.logout()
        service.current_user = {'ma_nguoi_dung': 2}
        service.browser_client.token = 'account-b'
        service._progress['score'] = 12
        release.set()
        with pytest.raises(ApiClientError, match='thay đổi'):
            await task
        assert service._progress['score'] == 12
        assert service.current_user['ma_nguoi_dung'] == 2
        assert not service.network_errors
    asyncio.run(run())


def test_old_task_error_does_not_pollute_new_account():
    async def run():
        service = ApiGameDataService('http://unused')
        entered, release = asyncio.Event(), asyncio.Event()

        async def old_operation():
            entered.set()
            try:
                await release.wait()
            except asyncio.CancelledError:
                # Mô phỏng transport đã gửi request và hoàn tất bất chấp hủy task.
                await release.wait()
            raise ApiClientError('Lỗi của phiên A')

        task = service._schedule(old_operation())
        await entered.wait()
        service.network_errors.append('Lỗi cũ')
        service.logout()
        release.set()
        await asyncio.gather(task, return_exceptions=True)
        await asyncio.sleep(0)
        assert service.network_errors == []
        assert service.save_state == 'confirmed'
    asyncio.run(run())