"""Entry point riêng của harness: barrier trước commit, không import từ production.

Không mở endpoint điều khiển; tín hiệu qua thư mục tạm do process cha sở hữu.
"""
from __future__ import annotations

import inspect
import os
from pathlib import Path
import time


def main() -> None:
    import uvicorn
    from task5.server import repository

    directory = Path(os.environ['TASK5_TRANSACTION_BARRIER']).resolve()
    target = os.environ['TASK5_TRANSACTION_FUNCTION']
    if target not in {'save_progress','submit_answer','collect_clue','complete_quest','retry_review'}:
        raise ValueError('Hàm transaction không hợp lệ')
    original = repository._connect
    used = False

    class Connection:
        def __init__(self, connection):
            self.connection = connection

        def __getattr__(self, name):
            return getattr(self.connection, name)

        def commit(self):
            nonlocal used
            if not used and any(frame.function == target for frame in inspect.stack()):
                used = True
                assert self.connection.in_transaction
                (directory/'entered').write_text('transaction-open', encoding='ascii')
                deadline = time.monotonic()+45
                while not (directory/'release').exists():
                    if time.monotonic() > deadline:
                        raise RuntimeError('Barrier kiểm thử hết hạn')
                    time.sleep(.02)
                if os.environ.get('TASK5_TRANSACTION_ROLLBACK') == '1':
                    self.connection.rollback()
                    (directory/'finished').write_text('rollback', encoding='ascii')
                    raise repository.RepositoryError('Rollback kiểm thử có kiểm soát')
                self.connection.commit()
                (directory/'finished').write_text('commit', encoding='ascii')
                return
            self.connection.commit()

    repository._connect = lambda: Connection(original())
    uvicorn.run('task5.server.app:app', host='127.0.0.1', port=int(os.environ['TASK5_TEST_PORT']))


if __name__ == '__main__':
    main()