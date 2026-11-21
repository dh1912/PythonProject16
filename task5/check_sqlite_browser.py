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
                        page.goto(url+'/web/',wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true',timeout=90000)
                        result=page.evaluate('''async () => {
                          async function api(path,data,token) {
                            const r=await fetch(path,{method:data===null?'GET':'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(data===null?{}:{body:JSON.stringify(data)})});
                            const body=await r.json();if(!r.ok)throw Error(path+JSON.stringify(body));return body;
                          }
                          const credentials={username:'browser_student',password:'test-password-123'};
                          const user=await api('/auth/register',{...credentials,fullname:'Browser Student'});
                          let token=user.access_token;
                          const content=await api('/game/content',null,token);
                          const location=content.locations.find(x=>x.id===1);
                          const qs=content.questions[location.name];
                          if(!qs.length)throw Error('No DB questions');
                          const q=qs[0];
                          await api('/quiz/submit',{ma_cau_hoi:q.id,dap_an_chon:(q.answer+1)%4,so_giay:30},token);
                          const review=await api('/review/me',null,token);
                          if(!review.items.length)throw Error('No review item');
                          const first=await api('/review/retry',{ma_cau_hoi:q.id,dap_an_chon:q.answer},token);
                          const repeat=await api('/review/retry',{ma_cau_hoi:q.id,dap_an_chon:q.answer},token);
                          if(first.points_awarded!==15||repeat.points_awarded!==0)throw Error('Duplicate review reward');
                          for(const item of qs)await api('/quiz/submit',{ma_cau_hoi:item.id,dap_an_chon:item.answer,so_giay:30},token);
                          const clues=content.investigation_data[location.name].clues.map(c=>c.id);
                          await api('/progress/save',{current_loc_id:1,max_year:1914,completed:[],task4:{'1':{clue_ids:clues,quiz_attempts:0}}},token);
                          const completed=await api('/quest/complete',{ma_dia_diem:1,ten_dia_diem:location.name,nam_mo_khoa:1914},token);
                          const again=await api('/quest/complete',{ma_dia_diem:1,ten_dia_diem:location.name,nam_mo_khoa:1914},token);
                          if(again.bonus!==0)throw Error('Duplicate quest reward');
                          const login=await api('/auth/login',credentials);token=login.access_token;
                          const restored=(await api('/progress/me',null,token)).data;
                          if(restored.score!==completed.total_score||!restored.completed.includes(location.name))throw Error('Restore failed');
                          const board=await api('/leaderboard',null,token);
                          return {register:true,review_once:true,quiz:true,clues:true,quest_once:true,relogin_restore:true,leaderboard:Array.isArray(board.leaderboard),score:restored.score};
                        }''')
                        # UI thật dùng tài khoản đã được tạo bởi request thật trên DB tạm.
                        page.wait_for_timeout(1500)
                        canvas=page.locator('#canvas')
                        def click(x,y):
                            box=canvas.bounding_box(); w,h=canvas.evaluate('c=>[c.width,c.height]');scale=min(w/1080,h/720)
                            canvas.click(position={'x':((w-1080*scale)/2+x*scale)*box['width']/w,'y':((h-720*scale)/2+y*scale)*box['height']/h})
                        click(500,280);page.keyboard.type('browser_student',delay=80)
                        click(500,355);page.keyboard.type('test-password-123',delay=80)
                        with page.expect_response(lambda r:r.url.endswith('/review/me'),timeout=15000): click(500,432)
                        page.wait_for_timeout(1800)
                        page.keyboard.press('n');page.wait_for_timeout(1000)
                        page.screenshot(path=str(root/'data/sqlite-notebook.png'))
                        page.keyboard.press('Escape');page.keyboard.press('b');page.wait_for_timeout(1800)
                        page.keyboard.press('Escape');page.wait_for_timeout(1200)
                        page.keyboard.press('l');page.wait_for_timeout(1200)
                        # Tài khoản mới cho quest UI: không giả completed hoặc gọi Game trực tiếp.
                        registration=page.request.post(url+'/auth/register',data={'username':'ui_student','password':'ui-test-password','fullname':'UI Student'})
                        assert registration.status==201
                        ui_headers={'Authorization':'Bearer '+registration.json()['access_token']}
                        # Mở trang mới: đồng thời kiểm tra game khởi tạo lại không mất DB.
                        page.reload(wait_until='domcontentloaded')
                        page.wait_for_function('window.task5GameReady === true',timeout=90000)
                        page.wait_for_timeout(1800)
                        click(500,280)
                        for _ in range(35):page.keyboard.press('Backspace')
                        page.keyboard.type('ui_student',delay=70)
                        click(500,355)
                        for _ in range(35):page.keyboard.press('Backspace')
                        page.keyboard.type('ui-test-password',delay=70)
                        with page.expect_response(lambda response:response.url.endswith('/review/me'),timeout=15000):click(500,432)
                        page.wait_for_timeout(1500)
                        content=page.request.get(url+'/game/content').json()
                        loc=next(item for item in content['locations'] if item['id']==1)
                        click(loc['x'],loc['y']);page.keyboard.press('Enter');page.wait_for_timeout(1000)
                        for index in range(len(content['investigation_data'][loc['name']]['clues'])):
                            page.keyboard.press(str(index+1));page.wait_for_timeout(200)
                            for choice in ('1','2','3'):
                                page.keyboard.press(choice);page.wait_for_timeout(250)
                        page.keyboard.press('d');page.wait_for_timeout(1000)
                        for q in content['questions'][loc['name']]:
                            with page.expect_response(lambda response:response.url.endswith('/quiz/submit'),timeout=15000):
                                page.keyboard.press(str(q['answer']+1))
                            page.wait_for_timeout(600)
                        for _ in range(40):
                            progress=page.request.get(url+'/progress/me',headers=ui_headers).json()['data']
                            if loc['name'] in progress['completed']:break
                            page.wait_for_timeout(250)
                        else:raise AssertionError('Quest UI chưa được xác nhận')
                        result['ui_quest_sqlite']=True
                        page.screenshot(path=str(root/'data/sqlite-browser.png'))
                        result.update(ui_login_notebook_leaderboard=True,page_errors=errors)
                        (root/'data/sqlite-browser-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
                        print(json.dumps(result));return 0 if not errors else 1
                    finally: browser.close()
            finally:
                server.terminate();server.wait(timeout=15)


if __name__=='__main__': raise SystemExit(main())