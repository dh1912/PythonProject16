"""Nâng nội dung chính thức 004 không DELETE bản cũ; ID mới cố định."""
import json
from pathlib import Path
import re


def migrate(conn):
    source=extract_official_sources(Path(__file__).resolve().parents[1])
    for table in ('moc_lich_su','nguon_lich_su','nhan_vat_lich_su','dia_diem'):
        for row in source[table]:
            columns=list(row)
            conn.execute(f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)}) ON CONFLICT DO NOTHING",tuple(row.values()))
    # Liên kết sự kiện 30 được chỉ định rõ trong 004, không tự suy diễn địa điểm khác.
    conn.execute('UPDATE su_kien_lich_su SET ma_dia_diem=9 WHERE ma_su_kien=30 AND ma_dia_diem IS NULL')
    for table,pk,base in (('manh_moi','ma_manh_moi',60000),('cau_hoi_on_tap','ma_cau_hoi',61000)):
        for row_index,row in enumerate(source[table]):
            row={pk:base+row_index+1,**row}
            key=f'migration004:{table}:{row_index+1}'
            mapped=conn.execute('SELECT row_id FROM content_manifest WHERE source_key=?',(key,)).fetchone()
            if mapped:
                row[pk]=mapped['row_id']
                continue
            columns=list(row)
            # Dải riêng để giữ nguyên PK legacy và mọi FK người chơi hiện có.
            conn.execute(f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",tuple(row.values()))
            row[pk]=conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.execute('INSERT INTO content_manifest VALUES(?,?,?)',(key,table,row[pk]))


def extract_mysql_insert(sql_text: str, table: str) -> list[dict]:
    """Trích đúng INSERT từ dump; parser nhận multiline, escaped quote và semicolon trong text."""
    import ast
    match = re.search(rf"INSERT\s+INTO\s+`{re.escape(table)}`\s*\((.*?)\)\s*VALUES\s*", sql_text, re.I|re.S)
    if not match:
        return []
    columns = re.findall(r"`([^`]+)`", match.group(1))
    text = sql_text[match.end():]
    rows=[]; row=[]; token=[]; in_string=False; depth=0; position=0
    while position<len(text):
        ch=text[position]
        if in_string:
            token.append(ch)
            if ch=='\\' and position+1<len(text):
                position+=1;token.append(text[position])
            elif ch=="'":
                if position+1<len(text) and text[position+1]=="'":
                    position+=1;token.append(text[position])
                else: in_string=False
        elif ch=="'":in_string=True;token.append(ch)
        elif ch=='(':
            depth+=1
            if depth==1:row=[];token=[]
            else:token.append(ch)
        elif ch==')':
            if depth==1:
                raw=''.join(token).strip()
                row.append(_mysql_value(raw))
                if len(row)!=len(columns):raise ValueError(f"Sai số cột trong INSERT {table}: {len(row)} != {len(columns)}")
                rows.append(dict(zip(columns,row)));depth=0
                position+=1  # bỏ qua ')' đóng tuple, không parse biểu thức ON DUPLICATE
                if text[position:].lstrip().upper().startswith('ON DUPLICATE KEY UPDATE'):
                    break
                continue
            else:token.append(ch);depth-=1
        elif ch==',' and depth==1:
            row.append(_mysql_value(''.join(token).strip()));token=[]
        elif ch==';' and depth==0:
            break
        elif depth:token.append(ch)
        position+=1
    return rows


def _mysql_value(raw: str):
    if raw.upper()=='NULL':return None
    if raw.upper() in ('TRUE','FALSE'):return int(raw.upper()=='TRUE')
    if raw.startswith("'") and raw.endswith("'"):
        body=raw[1:-1].replace("''", "'")
        return re.sub(r"\\([\\'\"nrt0])",lambda m:{'n':'\n','r':'\r','t':'\t','0':'\0'}.get(m.group(1),m.group(1)),body)
    try:return int(raw)
    except ValueError:
        try:return float(raw)
        except ValueError:return raw


def extract_official_sources(repo_root: Path) -> dict[str,list[dict]]:
    """Seed đóng gói cùng ứng dụng; runtime deploy không gọi Git hoặc phụ thuộc commit."""
    source_file=Path(__file__).parent/'historical_seed.json'
    source=json.loads(source_file.read_text(encoding='utf-8'))
    source.update(json.loads((Path(__file__).parent/'historical_v6.json').read_text(encoding='utf-8')))
    return source


def active_rows(conn,table,rows):
    """Ẩn bộ legacy bị 004 thay thế khỏi nội dung mới, nhưng giữ nguyên bản ghi/ID."""
    pk={'manh_moi':'ma_manh_moi','cau_hoi_on_tap':'ma_cau_hoi'}[table]
    manifest=conn.execute('SELECT row_id FROM content_manifest WHERE table_name=?',(table,)).fetchall()
    ids={r['row_id'] for r in manifest}
    return [r for r in rows if r.get('ma_su_kien') not in {20,25,29,30} or r[pk] in ids]