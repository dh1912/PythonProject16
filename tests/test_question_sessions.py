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