"""Nghiệm thu SQLite thật trên file tạm; không mock repository hoặc DB nhóm."""
import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from data import db_queries as db
from data.sqlite_store import connect, initialize
from task5.server import repository as repo
from task5.server.auth import password_hash


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / 'game.db'
    monkeypatch.setenv('SQLITE_DB_PATH', str(path))
    initialize(path)
    return path


def test_auth_password_and_legacy_reset(database):
    user, msg = db.register_user('student', 'test-password', 'Student')
    assert user, msg
    assert db.authenticate_user('student', 'test-password')[0]
    assert db.authenticate_user('student', 'wrong')[0] is None
    assert db.authenticate_user('missing', 'test-password')[0] is None
    assert db.register_user('student', 'test-password', 'Student')[0] is None
    c = connect()
    c.execute("INSERT INTO nguoi_dung(ten_dang_nhap,mat_khau_ma_hoa,ho_va_ten) VALUES('legacy','plaintext','Legacy')")
    c.commit(); c.close()
    assert db.authenticate_user('legacy','plaintext')[0] is None


def test_migration_keeps_users_progress_and_backup(database):
    user, _ = db.register_user('student','test-password','Student')
    uid = user['ma_nguoi_dung']
    assert db.save_user_progress(uid,1,1914,123,'[]',json.dumps({'_task5':{'correct_streak':2}}))[0]
    assert db.save_task4_progress(uid,1,'["1"]',3)[0]
    assert db.save_user_progress(uid,1,1914,124,'[]')[0]
    initialize(database)
    row, _ = db.fetch_user_progress(uid)
    state = json.loads(row['du_lieu_nhiem_vu'])
    assert row['diem_tri_thuc'] == 124
    assert state['_task5']['correct_streak'] == 2 and state['1']['clue_ids'] == ['1']
    c = connect(); c.execute('PRAGMA user_version=4'); c.close()
    initialize(database)
    assert list(database.parent.glob('game.db.backup-*'))
    assert db.fetch_user_progress(uid)[0]['diem_tri_thuc'] == 124


def test_sqlite_concurrency_quiz_review_quest_restart(database):
    user = repo.create_user('student',password_hash('test-password'),'Student')
    uid = user['ma_nguoi_dung']
    c = connect(); question = c.execute('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 1').fetchone(); c.close()
    qid = str(question['ma_cau_hoi']); answer = ord(question['dap_an_dung'])-65
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda _: repo.submit_answer(uid,qid,answer,30),range(3)))
    assert sorted(x['points_awarded'] for x in results) == [0,0,30]
    assert repo.load_progress(uid)['score'] == 30
    with pytest.raises(repo.RepositoryError): repo.submit_answer(uid,'9999999',0,30)
    assert repo.load_progress(uid)['score'] == 30
    c=connect(); second=c.execute('SELECT * FROM cau_hoi_on_tap WHERE ma_cau_hoi<>? ORDER BY ma_cau_hoi LIMIT 1',(int(qid),)).fetchone();c.close()
    q2=str(second['ma_cau_hoi']);a2=ord(second['dap_an_dung'])-65
    repo.submit_answer(uid,q2,(a2+1)%4,30)
    assert repo.list_reviews(uid)[0]['status'] == 'PENDING'
    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(lambda _:repo.retry_review(uid,q2,a2),range(2)))
    assert sorted(x['points_awarded'] for x in results)==[0,15]
    assert repo.list_reviews(uid)[0]['status']=='MASTERED'
    initialize(database)
    assert repo.retry_review(uid,q2,a2)['points_awarded']==0
    c=connect();assert c.execute('PRAGMA foreign_keys').fetchone()['foreign_keys']==1;c.close()


def test_http_real_sqlite(database, monkeypatch):
    from fastapi.testclient import TestClient
    from task5.server.app import app
    import task5.server.auth as auth
    monkeypatch.setattr(auth,'TASK5_JWT_SECRET','temporary-test-secret-at-least-32-characters')
    with TestClient(app) as client:
        assert client.get('/api/health').json()['database']=='sqlite'
        response=client.post('/auth/register',json={'username':'student','password':'test-password','fullname':'Student','vai_tro':'admin'})
        assert response.status_code==201,response.text
        assert response.json()['user']['vai_tro']=='nguoi_choi'
        assert 'password' not in response.text and 'mat_khau' not in response.text
        headers={'Authorization':'Bearer '+response.json()['access_token']}
        assert client.get('/teacher/report',headers=headers).status_code==403
        assert client.get('/progress/me',headers={'Authorization':'Bearer invalid'}).status_code==401
        assert client.post('/auth/login',json={'username':'student','password':'wrong'}).status_code==401
        assert client.post('/auth/login',json={'username':'student','password':'test-password'}).status_code==200
        import jwt
        expired=jwt.encode({'ma_nguoi_dung':response.json()['user']['ma_nguoi_dung'],'exp':0},auth.TASK5_JWT_SECRET,algorithm='HS256')
        assert client.get('/progress/me',headers={'Authorization':'Bearer '+expired}).status_code==401
        for resource in ('locations','events','clues','characters','questions'):
            assert client.get('/game/catalog/'+resource).json()['items']
        assert client.get('/game/catalog/nguoi_dung').status_code==404
        saved=client.post('/progress/save',headers=headers,json={'current_loc_id':1,'max_year':1914,'completed':[],'score':999999})
        assert saved.status_code==200
        assert client.get('/progress/me',headers=headers).json()['data']['score']==0


def test_restart_process_restores_progress(database):
    import subprocess, sys, os
    user, _ = db.register_user('restart','test-password','Restart')
    uid = user['ma_nguoi_dung']
    assert db.save_user_progress(uid,1,1914,123,'[]','{"_task5":{"correct_streak":3}}')[0]
    code = "from data.db_queries import fetch_user_progress; import json; r,m=fetch_user_progress("+str(uid)+"); assert r['diem_tri_thuc']==123; assert json.loads(r['du_lieu_nhiem_vu'])['_task5']['correct_streak']==3; print('RESTORE_PASS')"
    result = subprocess.run([sys.executable,'-c',code], env=os.environ.copy(), capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    assert 'RESTORE_PASS' in result.stdout


def test_teacher_report_and_invalid_health(database, monkeypatch):
    from fastapi.testclient import TestClient
    from task5.server.app import app
    import task5.server.auth as auth
    monkeypatch.setattr(auth,'TASK5_JWT_SECRET','temporary-test-secret-at-least-32-characters')
    teacher = repo.create_user('teacher',password_hash('test-password'),'Teacher')
    conn=connect();conn.execute("UPDATE nguoi_dung SET vai_tro='teacher' WHERE ma_nguoi_dung=?",(teacher['ma_nguoi_dung'],));conn.commit();conn.close()
    with TestClient(app) as client:
        response=client.post('/auth/login',json={'username':'teacher','password':'test-password'})
        headers={'Authorization':'Bearer '+response.json()['access_token']}
        assert client.get('/teacher/report',headers=headers).status_code==200
        # DB path trỏ thư mục: health không được trả healthy giả.
        monkeypatch.setenv('SQLITE_DB_PATH',str(database.parent))
        assert client.get('/api/health').status_code==503


def test_existing_extra_tables_survive_and_seed_is_stable(database):
    conn=connect()
    before=conn.execute('SELECT COUNT(*) AS n FROM manh_moi').fetchone()['n']
    conn.execute('CREATE TABLE task4_custom(id INTEGER PRIMARY KEY, note TEXT)')
    conn.execute("INSERT INTO task4_custom VALUES(1,'keep')")
    conn.execute('PRAGMA user_version=4');conn.commit();conn.close()
    initialize(database);initialize(database)
    conn=connect()
    assert conn.execute('SELECT note FROM task4_custom').fetchone()['note']=='keep'
    assert conn.execute('SELECT COUNT(*) AS n FROM manh_moi').fetchone()['n']==before
    assert conn.execute('PRAGMA foreign_key_check').fetchall()==[]
    conn.close()


def test_migration_failure_preserves_existing_duplicate_progress(tmp_path,monkeypatch):
    import sqlite3
    path=tmp_path/'old.db';monkeypatch.setenv('SQLITE_DB_PATH',str(path))
    c=sqlite3.connect(path)
    c.execute('CREATE TABLE tien_do_choi(ma_nguoi_dung INTEGER,diem_tri_thuc INTEGER)')
    c.executemany('INSERT INTO tien_do_choi VALUES(?,?)',[(1,10),(1,20)])
    c.commit();c.close()
    with pytest.raises(sqlite3.IntegrityError):initialize(path)
    c=sqlite3.connect(path)
    assert c.execute('SELECT SUM(diem_tri_thuc) FROM tien_do_choi').fetchone()[0]==30
    assert c.execute('PRAGMA user_version').fetchone()[0]==0
    c.close()
    assert list(tmp_path.glob('old.db.backup-*'))


def test_real_quest_clues_idempotency_and_rollback(database):
    user=repo.create_user('quest_student',password_hash('test-password'),'Quest')
    uid=user['ma_nguoi_dung'];content=repo.load_game_content()
    location=next(item for item in content['locations'] if item['id']==1)
    with pytest.raises(repo.RepositoryError):repo.complete_quest(uid,1,'Fake',1975)
    with pytest.raises(repo.RepositoryError):repo.save_progress(uid,1,1975,['Dien Bien Phu'],{})
    for question in content['questions'][location['name']]:
        repo.submit_answer(uid,question['id'],question['answer'],30)
    with pytest.raises(repo.RepositoryError):repo.save_progress(uid,1,1914,[],{'1':{'clue_ids':['forged']}})
    clues=[item['id'] for item in content['investigation_data'][location['name']]['clues']]
    repo.save_progress(uid,1,1975,[],{'1':{'clue_ids':clues}})
    first=repo.complete_quest(uid,1,'Fake',1975)
    second=repo.complete_quest(uid,1,'Fake',1975)
    assert first['bonus']==30 and second['bonus']==0
    restored=repo.load_progress(uid)
    assert restored['completed']==[location['name']]
    assert restored['max_year']<1975
    assert '_task5' not in restored['task4']


def test_exception_after_insert_rolls_back_real_sqlite(database):
    from unittest.mock import patch
    import sqlite3
    user=repo.create_user('rollback_student',password_hash('test-password'),'Rollback')
    uid=user['ma_nguoi_dung'];c=connect()
    c.execute("CREATE TRIGGER refuse_score BEFORE UPDATE OF diem_tri_thuc ON tien_do_choi BEGIN SELECT RAISE(ABORT,'test rollback'); END")
    c.commit();q=c.execute('SELECT * FROM cau_hoi_on_tap LIMIT 1').fetchone();c.close()
    with pytest.raises(repo.RepositoryError,match='test rollback'):
        repo.submit_answer(uid,str(q['ma_cau_hoi']),ord(q['dap_an_dung'])-65,30)
    c=connect()
    assert c.execute('SELECT COUNT(*) AS n FROM answer_log WHERE ma_nguoi_dung=?',(uid,)).fetchone()['n']==0
    assert c.execute('SELECT diem_tri_thuc FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()['diem_tri_thuc']==0
    c.close()