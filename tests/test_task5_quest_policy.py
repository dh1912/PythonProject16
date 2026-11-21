"""Chính sách server giữ đúng quy tắc mở khóa hiện có, không sửa Task 4."""
from unittest.mock import patch
import pytest
from task5.server.quest_policy import unlocked_names, validate_progress
from task5.server import repository as repo
from task4.quest_system import QuestManager
from tests.test_task5_repository import connection

LOCATIONS = [
    {"id": 1, "name": "Ben Nha Rong", "start": 1914},
    {"id": 2, "name": "Hong Kong", "start": 1930},
    {"id": 6, "name": "Ba Dinh", "start": 1941},
    {"id": 7, "name": "Viet Bac", "start": 1946},
    {"id": 8, "name": "Dien Bien Phu", "start": 1953},
]


@pytest.mark.parametrize("completed", [set(), {"Ben Nha Rong"}, {"Ben Nha Rong", "Hong Kong", "Ba Dinh"}])
def test_server_unlock_matches_task4(completed):
    assert unlocked_names(LOCATIONS, completed) == QuestManager(LOCATIONS, completed).unlocked


def test_cannot_skip_or_claim_completed_through_save():
    with pytest.raises(ValueError, match="mở khóa"):
        validate_progress(LOCATIONS, set(), [], 8)
    with pytest.raises(ValueError, match="tự khai"):
        validate_progress(LOCATIONS, set(), ["Ben Nha Rong"], 1)
    assert validate_progress(LOCATIONS, set(), [], 1)["id"] == 1


def test_missing_clue_prevents_quest_award():
    conn, cursor = connection([
        {"diem_tri_thuc": 0, "danh_sach_dia_diem_da_mo": "[]", "du_lieu_nhiem_vu": '{"1":{"clue_ids":["1"]}}'},
        {"ma_dia_diem": 1, "ten_dia_diem": "Bến Nhà Rồng"},
    ])
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_location_catalog", return_value=LOCATIONS), patch.object(repo, "_required_clues", return_value={"1", "2"}):
        with pytest.raises(repo.RepositoryError, match="manh mối"):
            repo.complete_quest(1, 1, "Fake Name", 1975)
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()
    assert not any("INSERT INTO answer_log" in c.args[0] for c in cursor.execute.call_args_list)


def test_forged_completed_save_rolls_back():
    conn, cursor = connection([{"danh_sach_dia_diem_da_mo": "[]", "du_lieu_nhiem_vu": "{}"}])
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_location_catalog", return_value=LOCATIONS):
        with pytest.raises(repo.RepositoryError, match="tự khai"):
            repo.save_progress(1, 1, 1975, ["Dien Bien Phu"], {})
    conn.rollback.assert_called_once()


def test_valid_clues_merge_but_client_attempt_count_is_ignored():
    conn, cursor = connection([{"danh_sach_dia_diem_da_mo": "[]", "du_lieu_nhiem_vu": '{"1":{"clue_ids":["1"],"quiz_attempts":2}}'}])
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_location_catalog", return_value=LOCATIONS), patch.object(repo, "_required_clues", return_value={"1", "2"}):
        repo.save_progress(1, 1, 1914, [], {"1": {"clue_ids": ["2"], "quiz_attempts": 999}})
    import json
    update = next(c.args for c in cursor.execute.call_args_list if c.args[0].startswith("UPDATE"))
    saved = json.loads(update[1][3])
    assert saved["1"] == {"clue_ids": ["1", "2"], "quiz_attempts": 2}
    conn.commit.assert_called_once()