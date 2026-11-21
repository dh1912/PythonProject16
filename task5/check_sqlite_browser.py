"""Edge + FastAPI + SQLite thật trên file tạm; không HTTP mock hoặc dữ liệu nhóm."""
from __future__ import annotations
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request


def main() -> int:
    from playwright.sync_api import sync_playwright
    root = Path(__file__).resolve().parents[1]
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'): stream.reconfigure(encoding='utf-8', errors='replace')
    with tempfile.TemporaryDirectory(prefix='task5-sqlite-e2e-') as directory, socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
        env=os.environ.copy()
        env.update(SQLITE_DB_PATH=str(Path(directory)/'test.db'), JWT_SECRET=secrets.token_urlsafe(48),
                   WEB_BUILD_DIR=str(root/'build/web-source/build/web'), PYTHONUTF8='1')
        os.environ['SQLITE_DB_PATH']=env['SQLITE_DB_PATH']
        from data.sqlite_store import initialize
        initialize(Path(env['SQLITE_DB_PATH']))
        from data.sqlite_store import connect
        conn = connect()
        fixtures = {str(q['ma_cau_hoi']): ord(q['dap_an_dung'])-65
                    for q in conn.execute('SELECT * FROM cau_hoi_on_tap')}
        conn.close()
        from task4.timeline_data import TIMELINE_QUEST_CONFIGS
        timeline_payload={key:{'questions':[{'id':q['id'],'answer':q['answer']} for q in value['questions']]}
                          for key,value in TIMELINE_QUEST_CONFIGS.items()}
        sock.close()
        with (root/'data/sqlite-browser-server.log').open('w',encoding='utf-8') as log:
            server=subprocess.Popen([sys.executable,'-m','uvicorn','task5.server.app:app','--host','127.0.0.1','--port',str(port)],cwd=root,env=env,stdout=log,stderr=log)
            try:
                url=f'http://127.0.0.1:{port}'
                for _ in range(60):
                    try:
                        with urllib.request.urlopen(url+'/api/health',timeout=1): break
                    except OSError: time.sleep(.2)
                else: raise RuntimeError('API chưa sẵn sàng')
                with sync_playwright() as p:
                    browser=p.chromium.launch(channel='msedge',headless=True)
                    try:
                        page=browser.new_page(viewport={'width':1280,'height':900});errors=[]
                        page.on('pageerror',lambda exc:errors.append(str(exc)))
                        page.add_init_script('window.acceptanceTimeline='+json.dumps(timeline_payload,ensure_ascii=False)+';')
                        page.add_init_script('window.acceptanceAnswers='+json.dumps(fixtures)+';')
                        page.goto(url+'/web/',wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true',timeout=90000)
                        result=page.evaluate('''async () => {
                          async function api(path,data,token) {
                            const r=await fetch(path,{method:data===null?'GET':'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(data===null?{}:{body:JSON.stringify(data)})});
                            const body=await r.json();if(!r.ok)throw Error(path+JSON.stringify(body));return body;
                          }
                          const credentials={username:'e2e_'+Date.now(),password:'test-password-123'};
                          const user=await api('/auth/register',{...credentials,fullname:'Browser Student'});
                          let token=user.access_token;
                          const content=await api('/game/content',null,token);
                          for(const items of Object.values(content.questions))for(const q of items){
                            if('answer' in q)throw Error('Public answer leak');
                            q.answer=window.acceptanceAnswers[q.id];
                          }
                          const location=content.locations.find(x=>x.id===1);
                          const qs=content.questions[location.name];
                          const wrong=(qs[0].answer+1)%4;
                          await api('/quiz/submit',{ma_cau_hoi:qs[0].id,dap_an_chon:wrong,so_giay:30},token);
                          const review=await api('/review/me',null,token);
                          if(!review.items.some(x=>x.id===qs[0].id))throw Error('No review item');
                          const first=await api('/review/retry',{ma_cau_hoi:qs[0].id,dap_an_chon:qs[0].answer},token);
                          const repeat=await api('/review/retry',{ma_cau_hoi:qs[0].id,dap_an_chon:qs[0].answer},token);
                          if(first.points_awarded!==15||repeat.points_awarded!==0)throw Error('Duplicate review reward');
                          await api('/quest/complete',{ma_dia_diem:1,ten_dia_diem:location.name,nam_mo_khoa:1914},token).then(()=>{throw Error('Quest accepted without clues and required answers')}).catch(e=>{if(String(e).includes('Quest accepted'))throw e});
                          const completed=[];
                          const matrix=[];
                          // Theo QuestManager: mở quest chưa hoàn thành sớm nhất theo start.
                          const id_order=[1,2,3,4,5,6,7,8,9];
                          for(const id of id_order) {
                            const loc=content.locations.find(item=>item.id===id);
                            if(!loc)throw Error('Missing location id '+id);
                            const timeline=window.acceptanceTimeline[loc.name];
                            // ID timeline lấy từ bộ cấu hình Task 4; đáp án đúng do API tự tra cứu ở server.
                            const questions=timeline ? timeline.questions.map(q=>({id:'task4:'+q.id,answer:q.answer})) : content.questions[loc.name];
                            if(!questions || !questions.length)throw Error('Missing questions '+loc.name);
                            for(const q of questions) {
                              // Fixture chỉ chọn thao tác đúng; endpoint vẫn tự tra đáp án chuẩn để chấm.
                              const answer=q.answer;
                              if(!Number.isInteger(answer))throw Error('Server question ID unavailable '+q.id+' for '+loc.name);
                              await api('/quiz/submit',{ma_cau_hoi:q.id,dap_an_chon:answer,so_giay:30},token);
                            }
                            const clues=content.investigation_data[loc.name].clues.map(c=>c.id);
                            matrix.push({id:loc.id,name:loc.name,event_ids:(content.questions[loc.name]||[]).map(q=>q.id),
                              clue_ids:clues,timeline:!!timeline,timeline_question_ids:timeline?.questions.map(q=>q.id)||[]});
                            await api('/progress/save',{current_loc_id:loc.id,max_year:loc.start,completed:[...completed],task4:{[loc.id]:{clue_ids:clues,quiz_attempts:0}}},token);
                            const quest=await api('/quest/complete',{ma_dia_diem:loc.id,ten_dia_diem:loc.name,nam_mo_khoa:loc.start},token);
                            if(quest.bonus!==30)throw Error('Missing quest reward '+loc.name);
                            const duplicate=await api('/quest/complete',{ma_dia_diem:loc.id,ten_dia_diem:loc.name,nam_mo_khoa:loc.start},token);
                            if(duplicate.bonus!==0)throw Error('Duplicate quest bonus '+loc.name);
                            completed.push(loc.name);
                            const restored=(await api('/progress/me',null,token)).data;
                            if(!restored.completed.includes(loc.name))throw Error('Restore '+loc.name);
                          }
                          token=(await api('/auth/login',credentials)).access_token;
                          const restored=(await api('/progress/me',null,token)).data;
                          const board=(await api('/leaderboard',null,token)).leaderboard;
                          if(!Array.isArray(board)||restored.completed.length!==content.locations.length)throw Error('Leaderboard/restore failed');
                          return {register:true,review_once:true,quiz:true,clues:true,all_locations:completed,matrix,quest_once:true,relogin_restore:true,leaderboard:true,score:restored.score};
                        }''')
                        page.screenshot(path=str(root/'data/sqlite-browser.png'))
                        result['edge_fetch_sqlite_api']=True
                        result['page_errors']=errors
                        (root/'data/sqlite-browser-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
                        print(json.dumps(result))
                        return 0 if not errors else 1
                    finally:
                        browser.close()
            finally:
                server.terminate()
                server.wait(timeout=15)

if __name__=='__main__': raise SystemExit(main())