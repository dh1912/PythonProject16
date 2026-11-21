"""P0 với SQLite thật: không rò đáp án, bảo toàn state và mật khẩu nguyên vẹn."""
import json
from unittest.mock import Mock

import pygame
from fastapi.testclient import TestClient
from data.sqlite_store import connect, initialize
from task5.server import repository as repo
from task5.server.auth import password_hash
from task5.server.app import app
from scenes.login_scene import LoginScene


def test_public_endpoints_hide_answers(tmp_path, monkeypatch):
    monkeypatch.setenv('SQLITE_DB_PATH', str(tmp_path/'security.db'))
    initialize()
    with TestClient(app) as client:
        for path in ('/game/content', '/game/questions', '/game/catalog/questions'):
            response = client.get(path)
            assert response.status_code == 200
            def check(value):
                if isinstance(value, dict):
                    assert not {'answer','dap_an_dung','correct_index','explanation','giai_thich_chi_tiet'} & value.keys()
                    for item in value.values(): check(item)
                elif isinstance(value, list):
                    for item in value: check(item)
            check(response.json())


def test_collect_keeps_streak_and_other_tasks(tmp_path, monkeypatch):
    monkeypatch.setenv('SQLITE_DB_PATH', str(tmp_path/'streak.db'))
    initialize()
    user = repo.create_user('streak', password_hash(' password QĐ '), 'Test')
    uid = user['ma_nguoi_dung']
    conn = connect()
    questions = conn.execute('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 3').fetchall()
    for q in questions[:2]:
        repo.submit_answer(uid, str(q['ma_cau_hoi']), ord(q['dap_an_dung'])-65, 30)
    state_before = json.loads(conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()['du_lieu_nhiem_vu'])
    clue = conn.execute('SELECT * FROM manh_moi WHERE ma_manh_moi=1').fetchone()
    repo.collect_clue(uid,1,'1',clue['tieu_de_manh_moi'])
    state = json.loads(conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()['du_lieu_nhiem_vu'])
    assert state['_task5'] == state_before['_task5']
    assert state['_task5']['correct_streak'] == 2
    q=questions[2]
    assert repo.submit_answer(uid,str(q['ma_cau_hoi']),ord(q['dap_an_dung'])-65,30)['points_awarded'] == 36
    conn.close()
    from data.db_queries import authenticate_user
    assert authenticate_user('streak',' password QĐ ')[0]
    assert not authenticate_user('streak','password QĐ')[0]
    assert not authenticate_user('streak',' password qđ ')[0]


def test_form_preserves_password_spaces():
    pygame.init()
    scene=LoginScene()
    scene.data_service=Mock(async_auth_enabled=False)
    scene.data_service.login.return_value=(False,None,'test')
    scene.input_login_user.text='student'
    scene.input_login_pass.text=' Qq tiếng Việt '
    scene.do_login()
    scene.data_service.login.assert_called_once_with('student',' Qq tiếng Việt ')
    scene.data_service.register.return_value=(False,None,'test')
    scene.input_reg_user.text='student'
    scene.input_reg_name.text='Test'
    scene.input_reg_pass.text=' Qq tiếng Việt '
    scene.do_register()
    scene.data_service.register.assert_called_once_with('student',' Qq tiếng Việt ','Test')