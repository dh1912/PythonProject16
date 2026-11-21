"""Kiểm tra mọi đường đọc dùng manifest, không xóa dữ liệu legacy SQLite."""
from data import db_queries
from data.sqlite_store import connect, initialize
from task5.server import repository


def test_active_content_endpoints_keep_legacy(tmp_path, monkeypatch):
    monkeypatch.setenv('SQLITE_DB_PATH', str(tmp_path / 'active.db'))
    initialize()
    from fastapi.testclient import TestClient
    from task5.server.app import app
    from task5.server.auth import get_current_user

    conn = connect()
    before = conn.execute('SELECT COUNT(*) AS n FROM manh_moi').fetchone()['n']
    active_ids = {str(row['ma_manh_moi']) for row in db_queries.fetch_raw_manh_moi()[0]}
    question_ids = {str(row['ma_cau_hoi']) for row in db_queries.fetch_raw_cau_hoi()[0]}
    assert len(active_ids) < before
    content = repository.load_game_content()
    assert content['investigation_data']['Kinh Thanh Hue']['year'] == '1930'
    assert 'thành lập Đảng' in content['investigation_data']['Kinh Thanh Hue']['event']
    assert {str(row['ma_manh_moi']) for row in content['notebook']} == active_ids
    app.dependency_overrides[get_current_user] = lambda: {'ma_nguoi_dung': 1}
    try:
        with TestClient(app) as client:
            assert {str(r['ma_manh_moi']) for r in client.get('/notebook/clues').json()['items']} == active_ids
            assert {str(r['ma_manh_moi']) for r in client.get('/game/catalog/clues').json()['items']} == active_ids
            assert {str(r['ma_cau_hoi']) for r in client.get('/game/catalog/questions').json()['items']} == question_ids
            mapped = client.get('/game/questions').json()['questions']
            assert {q['id'] for items in mapped.values() for q in items} == question_ids
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        assert conn.execute('SELECT COUNT(*) AS n FROM manh_moi').fetchone()['n'] == before
        conn.close()