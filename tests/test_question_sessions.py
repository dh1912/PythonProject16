"""Phiên giờ server, SQLite thật và request đồng thời; không sửa công thức điểm."""
import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from data.sqlite_store import connect, initialize
from task5.server import repository as repo
from task5.server.auth import password_hash


@pytest.fixture
def context(tmp_path, monkeypatch):
    monkeypatch.setenv('SQLITE_DB_PATH',str(tmp_path/'sessions.db'))
    initialize()
    user=repo.create_user('session',password_hash('test-password'),'Test')
    c=connect()
    q=c.execute('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 1').fetchone()
    c.close()
    return user['ma_nguoi_dung'],str(q['ma_cau_hoi']),ord(q['dap_an_dung'])-65


def test_server_time_duplicate_concurrency_restart(context, monkeypatch):
    uid,qid,answer=context
    monkeypatch.setattr(repo.time,'time',lambda:1000)
    started=repo.start_question(uid,qid)
    assert started==repo.start_question(uid,qid)
    assert not {'answer','correct_index'} & started.keys()
    initialize()
    monkeypatch.setattr(repo.time,'time',lambda:1030)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:repo.submit_answer(uid,qid,answer,.25,started['session_id']),range(2)))
    assert sorted(r['points_awarded'] for r in results)==[0,30]
    assert repo.load_progress(uid)['score']==30
    with pytest.raises(repo.RepositoryError):repo.submit_answer(uid,qid,(answer+1)%4,30,started['session_id'])


def test_invalid_owner_question_expiry_and_rollback(context,monkeypatch):
    uid,qid,answer=context
    monkeypatch.setattr(repo.time,'time',lambda:1000)
    session=repo.start_question(uid,qid)['session_id']
    for user,question,sid in [(uid,qid,'missing'),(uid+1,qid,session),(uid,'2',session)]:
        with pytest.raises(repo.RepositoryError):repo.submit_answer(user,question,answer,30,sid)
    monkeypatch.setattr(repo.time,'time',lambda:4601)
    with pytest.raises(repo.RepositoryError):repo.submit_answer(uid,qid,answer,30,session)
    assert repo.load_progress(uid)['score']==0


def test_timeline_and_speed_formula(context, monkeypatch):
    uid,_,_=context
    q=repo._timeline_configs()['Pac Bo']['questions'][0]
    monkeypatch.setattr(repo.time,'time',lambda:1000)
    session=repo.start_question(uid,'task4:'+q['id'])['session_id']
    monkeypatch.setattr(repo.time,'time',lambda:1010)
    result=repo.submit_answer(uid,'task4:'+q['id'],q['answer'],.25,session)
    from task5.scoring_system import ScoringEngine
    assert result['points_awarded']==ScoringEngine().record_answer(True,10)


def test_http_legacy_no_speed_and_session_contract(context, monkeypatch):
    from fastapi.testclient import TestClient
    from task5.server.app import app
    from task5.server.auth import get_current_user
    uid,qid,answer=context
    app.dependency_overrides[get_current_user]=lambda:{'ma_nguoi_dung':uid}
    try:
        with TestClient(app,client=('session-test',50002)) as client:
            result=client.post('/quiz/submit',json={'ma_cau_hoi':qid,'dap_an_chon':answer,'so_giay':.25})
            assert result.status_code==200 and result.json()['points_awarded']==30
            started=client.post('/quiz/start',json={'ma_cau_hoi':'2'})
            assert started.status_code==200 and 'answer' not in started.json()
            invalid=client.post('/quiz/submit',json={'ma_cau_hoi':'2','dap_an_chon':0,'session_id':'x'*32})
            assert invalid.status_code==400
    finally:
        app.dependency_overrides.pop(get_current_user,None)


def test_migration_v7_backup_preserves_score(context):
    from data.sqlite_store import database_path
    uid,_,_=context
    c=connect()
    c.execute('UPDATE tien_do_choi SET diem_tri_thuc=123 WHERE ma_nguoi_dung=?',(uid,))
    c.execute('PRAGMA user_version=6')
    c.commit();c.close()
    initialize();initialize()
    assert repo.load_progress(uid)['score']==123
    path=database_path()
    assert list(path.parent.glob(path.name+'.backup-v7-*'))