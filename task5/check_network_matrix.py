"""Browser fetch thật + FastAPI/SQLite tạm; interception chỉ gây lỗi vận chuyển.

Không coi đây là kiểm thử HUD/Pygame: ghi rõ phạm vi trong JSON ma trận.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import secrets
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request


def main() -> int:
    from playwright.sync_api import sync_playwright
    root=Path(__file__).resolve().parents[1]
    matrix=[]
    with tempfile.TemporaryDirectory(prefix='task5-network-') as directory:
        path=Path(directory)/'matrix.db'
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        env=dict(os.environ,SQLITE_DB_PATH=str(path),JWT_SECRET=secrets.token_urlsafe(48),PYTHONUTF8='1')
        with (root/'data/network-server.log').open('w',encoding='utf-8') as log:
            server=subprocess.Popen([sys.executable,'-m','uvicorn','task5.server.app:app','--host','127.0.0.1','--port',str(port)],cwd=root,env=env,stdout=log,stderr=log)
            try:
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(url+'/api/health',timeout=1):break
                    except OSError:time.sleep(.2)
                else:raise RuntimeError('API chưa sẵn sàng')
                with sync_playwright() as pw:
                    browser=pw.chromium.launch(headless=True,**({'channel':'msedge'} if sys.platform=='win32' else {}))
                    try:
                        page=browser.new_page();errors=[]
                        page.on('pageerror',lambda exc:errors.append(str(exc)))
                        page.goto(url+'/api/health')
                        # Token chỉ trong JS memory; không trace/payload/log hoặc lưu xuống artifact.
                        def call(endpoint,payload=None,timeout=3000):
                            return page.evaluate('''async a => {
                              const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),a.timeout);
                              try {const r=await fetch(a.path,{method:a.payload===null?'GET':'POST',signal:controller.signal,
                                headers:{'Content-Type':'application/json',...(window.auth?{Authorization:'Bearer '+window.auth}:{})},
                                ...(a.payload===null?{}:{body:JSON.stringify(a.payload)})});
                                const b=await r.json();if(b.access_token)window.auth=b.access_token;
                                delete b.access_token;return {status:r.status,body:b};
                              }catch(e){return {status:0,error:e.name};}finally{clearTimeout(timer);}
                            }''',{'path':endpoint,'payload':payload,'timeout':timeout})
                        credentials={'username':'network_'+secrets.token_hex(5),'password':secrets.token_urlsafe(18)}
                        assert call('/auth/register',{**credentials,'fullname':'Network Test'})['status']==201
                        assert call('/auth/login',credentials)['status']==200
                        c=sqlite3.connect(path)
                        qid,answer=c.execute('SELECT ma_cau_hoi,dap_an_dung FROM cau_hoi_on_tap ORDER BY ma_cau_hoi LIMIT 1').fetchone()
                        qid=str(qid);answer=ord(answer)-65
                        content=call('/game/content')['body'];loc=content['locations'][0]
                        clues=content['investigation_data'][loc['name']]['clues']
                        def cut_after_commit(route):
                            response=route.fetch()
                            assert response.ok, f'Backend refused {route.request.url.split(url)[-1]}'
                            route.abort('connectionfailed')
                        def lost(endpoint,payload):
                            page.route('**'+endpoint,cut_after_commit,times=1)
                            assert call(endpoint,payload)['status']==0
                            matrix.append({'operation':endpoint,'case':'C commit rồi mất response','result':'PASS'})
                        # Start bị mất response: gọi lại trả đúng phiên SQLite đã tồn tại.
                        lost('/quiz/start',{'ma_cau_hoi':qid})
                        sid=c.execute('SELECT session_id FROM question_sessions WHERE ma_cau_hoi=?',(qid,)).fetchone()[0]
                        assert call('/quiz/start',{'ma_cau_hoi':qid})['body']['session_id']==sid
                        # Quiz sai thực -> review, mất response review không được thưởng lặp.
                        assert call('/quiz/submit',{'ma_cau_hoi':qid,'session_id':sid,'dap_an_chon':(answer+1)%4})['status']==200
                        lost('/review/retry',{'ma_cau_hoi':qid,'dap_an_chon':answer})
                        assert call('/review/retry',{'ma_cau_hoi':qid,'dap_an_chon':answer})['body']['points_awarded']==0
                        sid=call('/quiz/start',{'ma_cau_hoi':qid})['body']['session_id']
                        quiz={'ma_cau_hoi':qid,'session_id':sid,'dap_an_chon':answer}
                        lost('/quiz/submit',quiz)
                        score=call('/progress/me')['body']['data']['score']
                        assert call('/quiz/submit',quiz)['body']['points_awarded']==0
                        assert call('/progress/me')['body']['data']['score']==score
                        for clue in clues:
                            lost('/clues/collect',{'ma_dia_diem':1,'ma_manh_moi':clue['id'],'tu_lieu_chon':clue['name']})
                        save={'current_loc_id':1,'max_year':1914,'completed':[],
                              'task4':{'1':{'clue_ids':[x['id'] for x in clues]}}}
                        lost('/progress/save',save)
                        quest={'ma_dia_diem':1,'ten_dia_diem':loc['name'],'nam_mo_khoa':1914}
                        lost('/quest/complete',quest)
                        assert call('/quest/complete',quest)['body']['bonus']==0
                        assert loc['name'] in call('/progress/me')['body']['data']['completed']
                        # Offline và ngắt trước server: không có mutation SQLite.
                        before=call('/progress/me')['body']['data']
                        page.context.set_offline(True)
                        assert call('/progress/save',save)['status']==0
                        page.context.set_offline(False)
                        matrix.append({'operation':'/progress/save','case':'A offline','result':'PASS'})
                        page.route('**/progress/save',lambda route:route.abort('connectionfailed'),times=1)
                        assert call('/progress/save',save)['status']==0
                        assert call('/progress/me')['body']['data']==before
                        matrix.append({'operation':'/progress/save','case':'B abort trước server','result':'PASS'})
                        # Mã lỗi thật từ backend: không fulfill response nghiệp vụ giả.
                        assert call('/quiz/submit',{'ma_cau_hoi':qid,'session_id':'x'*32,'dap_an_chon':answer})['status']==400
                        page.evaluate('window.auth=null')
                        assert call('/progress/save',save)['status']==401
                        assert call('/auth/login',credentials)['status']==200
                        matrix.extend([{'operation':'/quiz/submit','case':'D invalid session 400','result':'PASS'},
                                       {'operation':'/progress/save','case':'E anonymous 401','result':'PASS'}])
                        # Giữ SQLite writer thật để backend không ghi được: 503, không mock HTTP.
                        c.execute('PRAGMA busy_timeout=1000');c.execute('BEGIN IMMEDIATE')
                        assert call('/progress/save',save,timeout=22000)['status']==503
                        c.rollback()
                        matrix.append({'operation':'/progress/save','case':'F SQLite writer busy 503','result':'PASS'})
                        # Backend commit thật, trì hoãn response cho client timeout.
                        def delayed(route):
                            response=route.fetch()
                            time.sleep(.3)
                            try:route.fulfill(response=response)
                            except Exception:pass
                        page.route('**/progress/save',delayed,times=1)
                        assert call('/progress/save',save,timeout=100)['status']==0
                        assert call('/progress/me')['body']['data']==before
                        matrix.append({'operation':'/progress/save','case':'G timeout sau commit','result':'PASS'})
                        # Refresh bỏ token memory, login lại đọc cùng tiến độ.
                        page.reload();assert call('/auth/login',credentials)['status']==200
                        assert call('/progress/me')['body']['data']==before
                        matrix.append({'operation':'auth/progress','case':'refresh rồi login restore','result':'PASS'})
                        assert not errors,errors
                        assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
                        assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
                        c.close()
                        result={'matrix':matrix,'page_errors':errors,'scope':'Browser fetch thật; không chứng minh HUD/game scene fault matrix',
                                'not_tested':['toàn bộ tổ hợp endpoint x lỗi','logout pending/account switch UI','timeline canvas','HUD resize fault']}
                        (root/'data/network-matrix.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
                        print(json.dumps(result,ensure_ascii=True))
                        return 0
                    finally:browser.close()
            finally:
                server.terminate();server.wait(timeout=20)


if __name__=='__main__':raise SystemExit(main())