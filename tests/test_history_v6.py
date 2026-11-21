"""Migration 006 giữ nguyên bản ghi legacy và nghiệm thu mọi quest SQLite."""
import json
import pytest
from data.sqlite_store import initialize, connect
from task5.server import repository as repo
from task5.server.auth import password_hash


@pytest.fixture
def store(tmp_path,monkeypatch):
    path=tmp_path/'history.db';monkeypatch.setenv('SQLITE_DB_PATH',str(path));initialize(path)
    return path


def test_v6_counts_and_active_replacement(store):
    c=connect()
    counts={t:c.execute(f'SELECT COUNT(*) AS n FROM {t}').fetchone()['n'] for t in ['dia_diem','su_kien_lich_su','nhan_vat','manh_moi','cau_hoi_on_tap','moc_lich_su','nguon_lich_su','nhan_vat_lich_su']}
    assert counts==dict(dia_diem=9,su_kien_lich_su=30,nhan_vat=8,manh_moi=26,cau_hoi_on_tap=20,moc_lich_su=30,nguon_lich_su=30,nhan_vat_lich_su=21)
    assert c.execute('SELECT COUNT(*) AS n FROM content_manifest').fetchone()['n']==28
    assert c.execute('SELECT ma_dia_diem FROM su_kien_lich_su WHERE ma_su_kien=30').fetchone()['ma_dia_diem']==9
    assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
    c.close()


def test_migration_preserves_user_and_old_ids(store):
    user=repo.create_user('migration',password_hash('test-password'),'Test');uid=user['ma_nguoi_dung']
    c=connect();c.execute('UPDATE tien_do_choi SET diem_tri_thuc=123,du_lieu_nhiem_vu=? WHERE ma_nguoi_dung=?',('{"_task5":{"correct_streak":2},"4":{"clue_ids":["5"]}}',uid));c.execute('PRAGMA user_version=5');c.commit();c.close()
    initialize(store);initialize(store)
    c=connect();row=c.execute('SELECT * FROM tien_do_choi WHERE ma_nguoi_dung=?',(uid,)).fetchone()
    assert row['diem_tri_thuc']==123 and json.loads(row['du_lieu_nhiem_vu'])['4']['clue_ids']==['5']
    assert c.execute('SELECT 1 FROM manh_moi WHERE ma_manh_moi=5').fetchone()
    assert list(store.parent.glob('history.db.backup-v6-*'))
    c.close()


@pytest.mark.parametrize('route',['database','timeline'])
def test_every_official_location_completes_and_restores(store,route):
    user=repo.create_user('all_'+route,password_hash('test-password'),'Test');uid=user['ma_nguoi_dung']
    content=repo.load_game_content()
    for loc in sorted(content['locations'],key=lambda x:x['start']):
        questions=content['questions'].get(loc['name'],[])
        timeline=repo._timeline_configs().get(loc['name'])
        if route=='timeline' and timeline:
            for q in timeline['questions']:repo.submit_answer(uid,'task4:'+q['id'],q['answer'],30)
        else:
            assert questions,loc
            for q in questions:repo.submit_answer(uid,q['id'],q['answer'],30)
        clues=[c['id'] for c in content['investigation_data'][loc['name']]['clues']]
        progress=repo.load_progress(uid)
        repo.save_progress(uid,loc['id'],loc['start'],progress['completed'],{str(loc['id']):{'clue_ids':clues}})
        result=repo.complete_quest(uid,loc['id'],loc['name'],loc['start'])
        assert result['bonus']==30
        assert repo.complete_quest(uid,loc['id'],loc['name'],loc['start'])['bonus']==0
        assert loc['name'] in repo.load_progress(uid)['completed']