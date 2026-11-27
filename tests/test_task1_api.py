"""Tests for the standalone Task 1 progress APIs."""

import json

from fastapi.testclient import TestClient

from task1 import api_server
from task1 import fastapi_server


def test_fastapi_task1_health_save_load_and_leaderboard(tmp_path, monkeypatch):
    data_file = tmp_path / "progress.json"
    monkeypatch.setattr(fastapi_server, "DATA_FILE", data_file)
    client = TestClient(fastapi_server.app)

    assert client.get("/api/health").status_code == 200

    response = client.post(
        "/api/progress/save",
        json={
            "user_id": "alice",
            "user_name": "Alice",
            "score": 120,
            "completed": ["Pác Bó"],
            "max_year": 1941,
            "task4": {"quest": "done"},
        },
    )
    assert response.status_code == 200
    assert response.json()["saved_score"] == 120

    loaded = client.get("/api/progress/alice")
    assert loaded.status_code == 200
    assert loaded.json()["data"]["score"] == 120
    assert loaded.json()["data"]["task4"] == {"quest": "done"}

    assert client.get("/api/leaderboard?limit=1").json()["leaderboard"][0]["user_id"] == "alice"
    assert data_file.exists()
    assert json.loads(data_file.read_text(encoding="utf-8"))["progress"]["alice"]["score"] == 120


def test_fastapi_task1_validation_and_corrupt_file_recovery(tmp_path, monkeypatch):
    data_file = tmp_path / "progress.json"
    data_file.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(fastapi_server, "DATA_FILE", data_file)
    client = TestClient(fastapi_server.app)

    assert client.post("/api/progress/save", json={"user_id": "", "score": 1}).status_code == 422
    assert client.post("/api/progress/save", json={"user_id": "alice", "score": -1}).status_code == 422
    assert client.get("/api/leaderboard?limit=0").status_code == 422
    assert client.get("/api/progress/new-user").status_code == 200


def test_zero_dependency_api_writes_atomically_and_round_trips(tmp_path, monkeypatch):
    data_file = tmp_path / "progress.json"
    monkeypatch.setattr(api_server, "DATA_FILE", str(data_file))
    api_server.save_db({"users": {}, "progress": {}, "leaderboard": []})
    api_server.save_db(
        {
            "users": {},
            "progress": {"1": {"user_id": "1", "score": 50}},
            "leaderboard": [{"user_id": "1", "score": 50}],
        }
    )

    assert json.loads(data_file.read_text(encoding="utf-8"))["progress"]["1"]["score"] == 50
    assert not list(tmp_path.glob("*.tmp"))
