"""HTTP nghiệm thu dữ liệu container qua restart; chỉ dùng tài khoản thử ngẫu nhiên."""
import argparse
import json
from pathlib import Path
import secrets
import urllib.request


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['create','restore']);parser.add_argument('--url',default='http://127.0.0.1:8000');parser.add_argument('--state',type=Path,required=True);args=parser.parse_args()
    def api(path,payload=None,token=None):
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        req=urllib.request.Request(args.url+path,data=None if payload is None else json.dumps(payload).encode(),headers=headers)
        with urllib.request.urlopen(req,timeout=15) as response:return json.load(response)
    assert api('/api/health')['database']=='sqlite'
    if args.mode=='create':
        state={'username':'ci_'+secrets.token_hex(6),'password':secrets.token_urlsafe(18)}
        registered=api('/auth/register',{**state,'fullname':'CI Test'})
        token=registered['access_token'];content=api('/game/content')
        loc=next(x for x in content['locations'] if x['id']==1)
        for q in content['questions'][loc['name']]:api('/quiz/submit',{'ma_cau_hoi':q['id'],'dap_an_chon':q['answer'],'so_giay':30},token)
        api('/progress/save',{'current_loc_id':1,'max_year':1914,'completed':[],'task4':{'1':{'clue_ids':[c['id'] for c in content['investigation_data'][loc['name']]['clues']]}}},token)
        api('/quest/complete',{'ma_dia_diem':1,'ten_dia_diem':loc['name'],'nam_mo_khoa':1914},token)
        state['expected']=api('/progress/me',token=token)['data']
        args.state.write_text(json.dumps(state),encoding='utf-8')
    else:
        state=json.loads(args.state.read_text(encoding='utf-8'))
        login=api('/auth/login',{'username':state['username'],'password':state['password']})
        assert api('/progress/me',token=login['access_token'])['data']==state['expected']
    print('SQLite container '+args.mode+' PASS')


if __name__=='__main__':main()