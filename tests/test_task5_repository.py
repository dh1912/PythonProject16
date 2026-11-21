"""Kiểm thử repository thật với cursor giả, không kết nối MySQL."""
import json
from unittest.mock import MagicMock, patch
from task5.server import repository as repo


def connection(rows):
    conn = MagicMock()
    cursor = conn.cursor.return_value
    cursor.fetchone.side_effect = rows
    return conn, cursor


def test_streak_is_restored_from_persisted_server_state():
    conn, cursor = connection([{"diem_tri_thuc": 30, "du_lieu_nhiem_vu": '{"_task5":{"correct_streak":1}}'}, None])
    question = {"answer": 1, "options": ["a", "b"], "explanation": "e", "source": "s"}
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_get_question", return_value=question):
        result = repo.submit_answer(1, "1", 1, 30)
    assert result["points_awarded"] == 33
    updates = [call.args for call in cursor.execute.call_args_list if "SET diem_tri_thuc=?,du_lieu_nhiem_vu" in call.args[0]]
    assert json.loads(updates[0][1][1])["_task5"]["correct_streak"] == 2
    conn.commit.assert_called_once()


def test_duplicate_answer_does_not_change_score():
    conn, cursor = connection([{"diem_tri_thuc": 54}, {"dung_sai": 1}])
    q = {"answer": 1, "options": ["a", "b"], "explanation": "e", "source": "s"}
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_get_question", return_value=q):
        result = repo.submit_answer(1, "1", 1, 30)
    assert result["points_awarded"] == 0
    assert result["total_score"] == 54
    assert not any("UPDATE tien_do_choi" in c.args[0] for c in cursor.execute.call_args_list)


def test_unknown_quest_rolls_back_without_award():
    import pytest
    conn, cursor = connection([{"diem_tri_thuc": 0}, None])
    with patch.object(repo, "_connect", return_value=conn), pytest.raises(repo.RepositoryError):
        repo.complete_quest(1, 999, "Fake", 1975)
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_save_rejects_overwriting_server_scoring_state():
    import pytest
    conn, cursor = connection([{"danh_sach_dia_diem_da_mo": "[]", "du_lieu_nhiem_vu": "{}"}])
    with patch.object(repo, "_connect", return_value=conn), pytest.raises(repo.RepositoryError):
        repo.save_progress(1, 1, 1914, [], {"_task5": {"correct_streak": 999}})
    conn.rollback.assert_called_once()


def test_leading_zero_question_id_uses_canonical_log_key():
    conn, cursor = connection([{"diem_tri_thuc": 54}, {"dung_sai": 1}])
    question = {"id": "42", "answer": 1, "options": ["a", "b"], "explanation": "e", "source": "s"}
    with patch.object(repo, "_connect", return_value=conn), patch.object(repo, "_get_question", return_value=question):
        result = repo.submit_answer(1, "042", 1, 30)
    assert result["duplicate"]
    lookup = next(c.args for c in cursor.execute.call_args_list if "SELECT dung_sai FROM answer_log" in c.args[0])
    assert lookup[1] == (1, "42")