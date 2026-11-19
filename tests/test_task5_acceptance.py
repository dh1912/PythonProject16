"""Nghiệm thu HTTP và quyền truy cập với repository giả; không dùng DB thật."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from task5.server.app import app
from task5.server.auth import get_current_user


def test_player_cannot_read_teacher_data():
    app.dependency_overrides[get_current_user] = lambda: {"ma_nguoi_dung": 1, "vai_tro": "nguoi_choi"}
    try:
        with patch("task5.server.repository._connect", side_effect=AssertionError("DB bị cấm trong test")):
            with TestClient(app) as client:
                assert client.get("/teacher").status_code == 403
                assert client.get("/teacher/report").status_code == 403
                assert client.get("/teacher/login").status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_teacher_can_read_report_and_rank():
    app.dependency_overrides[get_current_user] = lambda: {"ma_nguoi_dung": 2, "vai_tro": "giao_vien"}
    try:
        with patch("task5.server.repository.teacher_report", return_value=([{"ho_va_ten": "Học sinh", "diem_tri_thuc": 600}], [])):
            with TestClient(app) as client:
                response = client.get("/teacher/report")
                assert response.status_code == 200
                assert response.json()["students"][0]["rank"] == "A"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_leaderboard_filters_private_fields_and_health_has_no_db():
    with patch("task5.server.repository._connect", side_effect=AssertionError("DB bị cấm trong test")), patch(
        "task5.server.repository.leaderboard", return_value=[{"display_name": "A", "score": 100, "password_hash": "private", "ma_nguoi_dung": 1}]
    ):
        with TestClient(app) as client:
            assert client.get("/api/health").status_code == 200
            response = client.get("/leaderboard")
            assert response.status_code == 200
            assert response.json()["leaderboard"] == [{"display_name": "A", "score": 100}]