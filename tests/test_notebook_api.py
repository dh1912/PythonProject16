"""Notebook dùng provider trên web và không tăng tiến độ khi chỉ đọc."""
import sys
from unittest.mock import patch
from task4.clue_notebook_scene import ClueNotebookScene


def test_web_notebook_provider_never_opens_sqlite():
    rows=[{'ma_manh_moi':1,'tieu_de_manh_moi':'A'}]
    with patch.object(sys,'platform','emscripten'), patch('data.db_queries.get_db_connection',side_effect=AssertionError('Cấm truy cập DB')):
        scene=ClueNotebookScene(data_provider=lambda:rows)
        scene.load_all_clues()
        assert scene.current_clue==rows[0]
        assert scene.bookmarked==set()