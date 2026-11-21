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
import sqlite3


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


def test_http_exact_password_forged_score_and_streak(tmp_path, monkeypatch):
    monkeypatch.setenv('SQLITE_DB_PATH', str(tmp_path/'http.db'))
    import task5.server.auth as auth
    monkeypatch.setattr(auth,'TASK5_JWT_SECRET','isolated-security-secret-at-least-32-characters')
    with TestClient(app) as client:
        credentials={'username':'security','password':' Qq tiếng Việt '}
        registered=client.post('/auth/register',json={**credentials,'fullname':'Test'})
        assert registered.status_code == 201
        for wrong in ('Qq tiếng Việt',' qq tiếng việt '):
            assert client.post('/auth/login',json={**credentials,'password':wrong}).status_code == 401
        logged=client.post('/auth/login',json=credentials)
        assert logged.status_code == 200
        headers={'Authorization':'Bearer '+logged.json()['access_token']}
        conn=connect()
        q=conn.execute('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 1').fetchone()
        answer=ord(q['dap_an_dung'])-65
        forged=client.post('/quiz/submit',headers=headers,json={
            'ma_cau_hoi':str(q['ma_cau_hoi']),'dap_an_chon':(answer+1)%4,'so_giay':30,
            'correct':True,'points_awarded':100000,'total_score':100000})
        assert forged.status_code == 200
        assert not forged.json()['correct'] and forged.json()['total_score'] == 0
        correct=client.post('/quiz/submit',headers=headers,json={
            'ma_cau_hoi':str(q['ma_cau_hoi']),'dap_an_chon':answer,'so_giay':30})
        assert correct.status_code == 200 and correct.json()['total_score'] == 30
        saved=client.post('/progress/save',headers=headers,json={
            'current_loc_id':1,'max_year':1914,'completed':[],
            'task4':{'_task5':{'correct_streak':1000}}})
        assert saved.status_code >= 400
        uid=logged.json()['user']['ma_nguoi_dung']
        state=json.loads(conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()['du_lieu_nhiem_vu'])
        assert state['_task5']['correct_streak'] == 1
        restored=client.post('/auth/login',json=credentials)
        assert restored.status_code == 200 and restored.json()['progress']['score'] == 30
        state_after=json.loads(conn.execute('SELECT du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()['du_lieu_nhiem_vu'])
        assert state_after == state
        conn.close()


def test_wal_backup_restores_progress_and_state(tmp_path, monkeypatch):
    from data.sqlite_store import backup_database
    original=tmp_path/'original.db'
    monkeypatch.setenv('SQLITE_DB_PATH',str(original))
    initialize()
    user=repo.create_user('backup',password_hash(' QĐ password '),'Test')
    uid=user['ma_nguoi_dung']
    conn=connect()
    conn.execute('UPDATE tien_do_choi SET diem_tri_thuc=123,du_lieu_nhiem_vu=? WHERE ma_nguoi_dung=?',
                 ('{"_task5":{"correct_streak":3},"1":{"clue_ids":["1"]}}',uid))
    conn.commit()
    target=backup_database(tmp_path/'restore.sqlite')
    restored=sqlite3.connect(target)
    assert restored.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    row=restored.execute('SELECT diem_tri_thuc,du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()
    assert row[0]==123 and json.loads(row[1])['_task5']['correct_streak']==3
    restored.close()
    conn.close()