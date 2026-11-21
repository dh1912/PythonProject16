"""Repository SQLite: kết nối riêng và BEGIN IMMEDIATE cho từng transaction ghi."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from data import db_queries
from data.db_queries import get_db_connection
from task5.scoring_system import ScoringEngine

# API chỉ kết nối đúng một database từ cấu hình; không thử fallback database khác.



class RepositoryError(RuntimeError):
    pass


def load_game_content():
    """Nội dung chính thức SQLite, không dùng ID fallback để lưu/chấm điểm."""
    from services.game_data_service import transform_locations, transform_investigation_data, transform_deduction_questions
    conn = _connect()
    try:
        locations = conn.execute('SELECT * FROM dia_diem ORDER BY ma_dia_diem').fetchall()
        events = conn.execute('SELECT * FROM su_kien_lich_su ORDER BY ma_su_kien').fetchall()
        people = conn.execute('SELECT * FROM nhan_vat ORDER BY ma_nhan_vat').fetchall()
        clues = conn.execute('SELECT * FROM manh_moi ORDER BY ma_manh_moi').fetchall()
        questions = conn.execute('SELECT * FROM cau_hoi_on_tap ORDER BY ma_cau_hoi').fetchall()
        ids = {row['ma_dia_diem'] for row in locations}
        mapped = [row for row in transform_locations(locations, events) if row['id'] in ids]
        investigation = transform_investigation_data(locations, events, people, clues)
        for loc in mapped:
            event_ids = {e['ma_su_kien'] for e in events if e.get('ma_dia_diem') == loc['id']}
            investigation[loc['name']]['clues'] = [{'id':str(c['ma_manh_moi']),'name':c['tieu_de_manh_moi'],'detail':c['noi_dung_chi_tiet']} for c in clues if c.get('ma_su_kien') in event_ids]
        notebook = conn.execute('''SELECT m.*,e.ten_su_kien,e.nam_dien_ra,n.ten_nhan_vat,d.ten_dia_diem,d.khu_vuc
          FROM manh_moi m LEFT JOIN su_kien_lich_su e ON e.ma_su_kien=m.ma_su_kien
          LEFT JOIN nhan_vat n ON n.ma_nhan_vat=m.ma_nhan_vat LEFT JOIN dia_diem d ON d.ma_dia_diem=e.ma_dia_diem
          ORDER BY e.nam_dien_ra,m.thu_tu_timeline_dung,m.ma_manh_moi''').fetchall()
        return {'locations':mapped,'investigation_data':{loc['name']:investigation[loc['name']] for loc in mapped},
                'questions':transform_deduction_questions(events,questions),'notebook':notebook,
                'is_connected':True,'status_message':'Nội dung chính thức SQLite qua API'}
    finally:
        conn.close()


def _connect():
    conn, message = get_db_connection()
    if conn is None:
        raise RepositoryError(str(message))
    return conn


def _user(cursor, clause: str, value: Any):
    cursor.execute("SELECT ma_nguoi_dung,ten_dang_nhap,mat_khau_ma_hoa,ho_va_ten,vai_tro FROM nguoi_dung WHERE " + clause + " LIMIT 1", (value,))
    return cursor.fetchone()


def get_user(username: str):
    conn = _connect()
    try:
        c = conn.cursor()
        return _user(c, "ten_dang_nhap=?", username)
    finally: conn.close()


def get_user_by_id(user_id: int):
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute("SELECT ma_nguoi_dung,ten_dang_nhap,ho_va_ten,vai_tro FROM nguoi_dung WHERE ma_nguoi_dung=?", (user_id,))
        return c.fetchone()
    finally: conn.close()


def get_hash(user_id: int):
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM tai_khoan_bao_mat WHERE ma_nguoi_dung=?", (user_id,))
        row = c.fetchone()
        return row["password_hash"] if row else None
    finally: conn.close()


def set_hash(user_id: int, hashed: str):
    conn = _connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        c.execute("INSERT INTO tai_khoan_bao_mat (ma_nguoi_dung,password_hash) VALUES (?,?) ON CONFLICT(ma_nguoi_dung) DO UPDATE SET password_hash=excluded.password_hash", (user_id, hashed))
        conn.commit()
    except Exception as exc:
        conn.rollback(); raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def authenticate_legacy(username: str, password: str):
    """Tái sử dụng xác thực legacy ở data layer khi chưa có bcrypt."""
    user, _message = db_queries.authenticate_user(username, password)
    return user


def create_user(username: str, hashed: str, fullname: str):
    conn = _connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        if _user(c, "ten_dang_nhap=?", username): return None
        c.execute("INSERT INTO nguoi_dung (ten_dang_nhap,mat_khau_ma_hoa,ho_va_ten,vai_tro) VALUES (?,?,?,'player')", (username, hashed, fullname))
        uid = int(c.lastrowid)
        c.execute("INSERT INTO tai_khoan_bao_mat (ma_nguoi_dung,password_hash) VALUES (?,?)", (uid, hashed))
        c.execute("INSERT INTO tien_do_choi (ma_nguoi_dung,ma_dia_diem_hien_tai,nam_mo_khoa_cao_nhat,diem_tri_thuc,danh_sach_dia_diem_da_mo) VALUES (?,1,1914,0,'[]')", (uid,))
        conn.commit()
        return {"ma_nguoi_dung": uid, "ten_dang_nhap": username, "ho_va_ten": fullname, "vai_tro": "player"}
    except Exception as exc:
        conn.rollback(); raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def load_progress(user_id: int):
    # SELECT trực tiếp để API không gọi helper legacy có thể ALTER TABLE tự động.
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ma_dia_diem_hien_tai,nam_mo_khoa_cao_nhat,diem_tri_thuc,danh_sach_dia_diem_da_mo,du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?", (user_id,))
        row = cursor.fetchone()
    finally:
        conn.close()
    if not row: raise RepositoryError("Không tìm thấy tiến độ người chơi.")
    try: completed = json.loads(row.get("danh_sach_dia_diem_da_mo") or "[]")
    except (TypeError, ValueError): completed = []
    try: task4 = json.loads(row.get("du_lieu_nhiem_vu") or "{}")
    except (TypeError, ValueError): task4 = {}
    # Không gửi khóa server _task5 ra client để lần lưu sau không ghi trả nhầm.
    task4 = {str(key): value for key, value in task4.items() if str(key).isdigit() and isinstance(value, dict)} if isinstance(task4, dict) else {}
    return {"score": int(row.get("diem_tri_thuc") or 0), "current_loc_id": int(row.get("ma_dia_diem_hien_tai") or 1), "max_year": int(row.get("nam_mo_khoa_cao_nhat") or 1914), "completed": completed, "task4": task4}


def save_progress(user_id: int, current_loc_id: int, max_year: int, completed: list[str], task4: dict[str, Any]):
    conn = _connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        c.execute("SELECT diem_tri_thuc,danh_sach_dia_diem_da_mo,du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?", (user_id,))
        old = c.fetchone()
        if not old: raise RepositoryError("Thiếu tiến độ người chơi.")
        try: merged = set(json.loads(old.get("danh_sach_dia_diem_da_mo") or "[]"))
        except (ValueError, TypeError): merged = set()
        from .quest_policy import validate_progress
        catalog = _location_catalog(c)
        try:
            selected = validate_progress(catalog, merged, completed, current_loc_id)
        except ValueError as exc:
            raise RepositoryError(str(exc)) from exc
        try: old_task4 = json.loads(old.get("du_lieu_nhiem_vu") or "{}")
        except (ValueError, TypeError): old_task4 = {}
        # Không cho client ghi đè trạng thái chấm điểm nội bộ của server.
        for key, value in task4.items():
            if not str(key).isdigit() or not isinstance(value, dict):
                raise RepositoryError("Dữ liệu nhiệm vụ không hợp lệ.")
            try:
                validate_progress(catalog, merged, [], int(key))
            except ValueError as exc:
                raise RepositoryError(str(exc)) from exc
            allowed = _required_clues(c, int(key))
            incoming = value.get("clue_ids", [])
            if not isinstance(incoming, list) or not set(incoming).issubset(allowed):
                raise RepositoryError("Manh mối không thuộc địa điểm.")
            previous = old_task4.get(str(key), {})
            old_task4[str(key)] = {"clue_ids": sorted(set(previous.get("clue_ids", [])) | set(incoming)),
                                  "quiz_attempts": int(previous.get("quiz_attempts", 0))}
        # Năm chỉ được suy ra từ địa điểm đã mở, không lấy giá trị tự khai 1975.
        allowed_year = max([1914, int(selected["start"])] + [int(item["start"]) for item in catalog if item["name"] in merged])
        c.execute("UPDATE tien_do_choi SET ma_dia_diem_hien_tai=?,nam_mo_khoa_cao_nhat=MAX(nam_mo_khoa_cao_nhat,?),danh_sach_dia_diem_da_mo=?,du_lieu_nhiem_vu=? WHERE ma_nguoi_dung=?", (current_loc_id, allowed_year, json.dumps(sorted(merged), ensure_ascii=False), json.dumps(old_task4, ensure_ascii=False), user_id))
        conn.commit()
    except Exception as exc:
        conn.rollback(); raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def _location_catalog(cursor):
    from services.game_data_service import LOCATION_MAP_CONFIG
    cursor.execute("SELECT ma_dia_diem,ten_dia_diem FROM dia_diem ORDER BY ma_dia_diem")
    return [{"id": int(row["ma_dia_diem"]),
             "name": LOCATION_MAP_CONFIG.get(int(row["ma_dia_diem"]), {}).get("key", row["ten_dia_diem"]),
             "start": LOCATION_MAP_CONFIG.get(int(row["ma_dia_diem"]), {}).get("start", 1914)}
            for row in cursor.fetchall()]


def _required_clues(cursor, location_id: int) -> set[str]:
    """ID chính thức cùng định dạng transform_investigation_data hiện có."""
    cursor.execute("SELECT m.ma_manh_moi FROM manh_moi m JOIN su_kien_lich_su e ON e.ma_su_kien=m.ma_su_kien WHERE e.ma_dia_diem=?", (location_id,))
    return {str(row["ma_manh_moi"]) for row in cursor.fetchall()}


@lru_cache(maxsize=1)
def _timeline_configs():
    """Nạp dữ liệu Task 4 đúng một lần, không kéo giao diện vào server."""
    import importlib.util
    import sys
    from pathlib import Path
    from types import ModuleType
    folder = Path(__file__).resolve().parents[2] / "task4"
    package_name = "_task5_timeline_data"
    package = ModuleType(package_name)
    package.__path__ = [str(folder)]
    sys.modules[package_name] = package
    for child in ("quest_system", "timeline_data"):
        fullname = f"{package_name}.{child}"
        spec = importlib.util.spec_from_file_location(fullname, folder / f"{child}.py")
        if spec is None or spec.loader is None:
            raise RepositoryError("Không nạp được dữ liệu quiz Task 4.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[fullname] = module
        spec.loader.exec_module(module)
        setattr(package, child, module)
    return sys.modules[f"{package_name}.timeline_data"].TIMELINE_QUEST_CONFIGS


def _get_question(cursor, question_id: str):
    if question_id.startswith("task4:"):
        TIMELINE_QUEST_CONFIGS = _timeline_configs()
        raw_id = question_id.removeprefix("task4:")
        for name, cfg in TIMELINE_QUEST_CONFIGS.items():
            for q in cfg.get("questions", []):
                if q.get("id") == raw_id:
                    return {"id": question_id, "text": q["question"], "options": q["options"], "answer": int(q["answer"]), "explanation": q.get("explanation", ""), "source": q.get("source", "Nguồn chung: dữ liệu Task 4"), "location": name}
        raise RepositoryError("Không tìm thấy câu hỏi Task 4 trên máy chủ.")
    try: qid = int(question_id)
    except ValueError as exc: raise RepositoryError("Mã câu hỏi không hợp lệ.") from exc
    cursor.execute("SELECT q.ma_cau_hoi,q.noi_dung_cau_hoi,q.dap_an_a,q.dap_an_b,q.dap_an_c,q.dap_an_d,q.dap_an_dung,q.giai_thich_chi_tiet,e.nguon_trich_dan,e.ten_su_kien FROM cau_hoi_on_tap q LEFT JOIN su_kien_lich_su e ON e.ma_su_kien=q.ma_su_kien WHERE q.ma_cau_hoi=?", (qid,))
    row = cursor.fetchone()
    if not row: raise RepositoryError("Không tìm thấy câu hỏi trong CSDL.")
    ans = str(row["dap_an_dung"]).strip().upper()
    return {"id": str(qid), "text": row["noi_dung_cau_hoi"], "options": [row[x] for x in ("dap_an_a","dap_an_b","dap_an_c","dap_an_d")], "answer": ord(ans[0])-65, "explanation": row.get("giai_thich_chi_tiet") or "", "source": row.get("nguon_trich_dan") or "Nguồn chung: chưa có trích dẫn cho sự kiện này", "location": row.get("ten_su_kien") or ""}


def submit_answer(user_id: int, question_id: str, choice: int, seconds: float):
    conn = _connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        c.execute("SELECT diem_tri_thuc,du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?", (user_id,))
        progress = c.fetchone()
        if not progress: raise RepositoryError("Không tìm thấy tiến độ người chơi.")
        q = _get_question(c, question_id)
        # Chuẩn hóa ID từ nguồn server, ngăn nhận thưởng qua ID có số 0 đầu.
        question_id = str(q.get("id", question_id))
        if not 0 <= choice < len(q["options"]): raise RepositoryError("Đáp án chọn không hợp lệ.")
        correct = choice == q["answer"]
        c.execute("SELECT dung_sai FROM answer_log WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (user_id, question_id))
        prev = c.fetchone()
        score = int(progress.get("diem_tri_thuc") or 0)
        engine = ScoringEngine(score)
        state = json.loads(progress.get("du_lieu_nhiem_vu") or "{}")
        engine.correct_streak = max(0, int(state.get("_task5", {}).get("correct_streak", 0)))
        if prev:
            old_correct = bool(prev["dung_sai"])
            if old_correct or not correct:
                if not correct:
                    state['_task5'] = {'correct_streak': 0}
                    c.execute('UPDATE tien_do_choi SET du_lieu_nhiem_vu=? WHERE ma_nguoi_dung=?', (json.dumps(state,ensure_ascii=False),user_id))
                rank = engine.calculate_rank(score); conn.commit()
                return {"correct": correct, "duplicate": True, "points_awarded": 0, "total_score": score, "rank": rank, "rank_title": engine.TITLES[rank], "explanation": q["explanation"], "source": q["source"]}
            # Đáp án sai trước đó đã bị phạt một lần; đúng lại nhận điểm đúng.
            delta = engine.record_answer(True, seconds)
            c.execute("UPDATE answer_log SET dung_sai=1,diem=?,thoi_gian=? WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (delta, seconds, user_id, question_id))
        else:
            delta = engine.record_answer(correct, seconds)
            c.execute("INSERT INTO answer_log (ma_nguoi_dung,ma_cau_hoi,dung_sai,diem,thoi_gian) VALUES (?,?,?,?,?)", (user_id, question_id, int(correct), delta, seconds))
            if not correct:
                c.execute("INSERT INTO review_items (ma_nguoi_dung,ma_cau_hoi,location_name,question_text,options_json,correct_index,user_choice,explanation,source_title,source_citation) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(ma_nguoi_dung,ma_cau_hoi) DO UPDATE SET user_choice=excluded.user_choice,retry_count=retry_count+1,status='PENDING'", (user_id, question_id, q["location"], q["text"], json.dumps(q["options"], ensure_ascii=False), q["answer"], choice, q["explanation"], q["source"], q["source"]))
        state["_task5"] = {"correct_streak": engine.correct_streak}
        c.execute("UPDATE tien_do_choi SET diem_tri_thuc=?,du_lieu_nhiem_vu=? WHERE ma_nguoi_dung=?", (engine.total_score, json.dumps(state, ensure_ascii=False), user_id))
        conn.commit()
        rank = engine.calculate_rank(engine.total_score)
        return {"correct": correct, "duplicate": False, "points_awarded": delta, "total_score": engine.total_score, "rank": rank, "rank_title": engine.TITLES[rank], "explanation": q["explanation"], "source": q["source"]}
    except Exception as exc:
        conn.rollback()
        if isinstance(exc, RepositoryError): raise
        raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def leaderboard(limit: int = 10):
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute("SELECT u.ho_va_ten AS display_name,p.diem_tri_thuc AS score FROM tien_do_choi p JOIN nguoi_dung u ON u.ma_nguoi_dung=p.ma_nguoi_dung ORDER BY p.diem_tri_thuc DESC LIMIT ?", (limit,))
        return c.fetchall()
    finally: conn.close()


def complete_quest(user_id: int, location_id: int, location_name: str, max_year: int):
    """Cộng thưởng quest +30 đúng một lần, đồng thời lưu tiến độ quest."""
    conn = _connect()
    key = f"quest_bonus:{int(location_id)}"
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        c.execute("SELECT diem_tri_thuc,danh_sach_dia_diem_da_mo,du_lieu_nhiem_vu FROM tien_do_choi WHERE ma_nguoi_dung=?", (user_id,))
        progress = c.fetchone()
        if not progress:
            raise RepositoryError("Không tìm thấy tiến độ người chơi.")
        # Không tin ID/tên/năm do client gửi để cấp thưởng quest.
        c.execute("SELECT ma_dia_diem,ten_dia_diem FROM dia_diem WHERE ma_dia_diem=?", (location_id,))
        location = c.fetchone()
        if not location:
            raise RepositoryError("Địa điểm không tồn tại.")
        from .quest_policy import validate_progress
        catalog = _location_catalog(c)
        saved_completed = set(json.loads(progress.get("danh_sach_dia_diem_da_mo") or "[]"))
        try:
            validate_progress(catalog, saved_completed, [], location_id)
        except ValueError as exc:
            raise RepositoryError(str(exc)) from exc
        required_clues = _required_clues(c, location_id)
        saved_tasks = json.loads(progress.get("du_lieu_nhiem_vu") or "{}")
        collected = set(saved_tasks.get(str(location_id), {}).get("clue_ids", []))
        if not required_clues.issubset(collected):
            raise RepositoryError("Chưa lưu đủ manh mối chính thức của địa điểm.")
        c.execute("SELECT q.ma_cau_hoi FROM cau_hoi_on_tap q JOIN su_kien_lich_su e ON e.ma_su_kien=q.ma_su_kien WHERE e.ma_dia_diem=?", (location_id,))
        required = {str(row["ma_cau_hoi"]) for row in c.fetchall()}
        # Có hai đường chơi hợp lệ: deduction DB hoặc quiz timeline Task 4.
        from services.game_data_service import LOCATION_MAP_CONFIG
        canonical = LOCATION_MAP_CONFIG.get(location_id, {}).get("key", "")
        timeline = _timeline_configs().get(canonical)
        timeline_required = {"task4:" + q["id"] for q in timeline["questions"]} if timeline else set()
        if not required and not timeline_required:
            raise RepositoryError("Địa điểm chưa có bộ câu hỏi để xác minh hoàn thành.")
        c.execute("SELECT ma_cau_hoi FROM answer_log WHERE ma_nguoi_dung=? AND dung_sai=1", (user_id,))
        answered = {str(row["ma_cau_hoi"]) for row in c.fetchall()}
        if not ((required and required.issubset(answered)) or (timeline_required and timeline_required.issubset(answered))):
            raise RepositoryError("Chưa trả lời đúng đủ câu hỏi của địa điểm.")
        # Chỉ xác minh ID và tiến độ đã lưu; chưa chứng minh người chơi đọc nội dung.
        location_name = canonical or location["ten_dia_diem"]
        c.execute("SELECT MAX(nam_dien_ra) AS max_year FROM su_kien_lich_su WHERE ma_dia_diem=?", (location_id,))
        event = c.fetchone() or {}
        max_year = int(event.get("max_year") or 1914)
        score = int(progress.get("diem_tri_thuc") or 0)
        try: completed = set(json.loads(progress.get("danh_sach_dia_diem_da_mo") or "[]"))
        except (TypeError, ValueError): completed = set()
        c.execute("SELECT 1 FROM answer_log WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (user_id, key))
        duplicate = c.fetchone() is not None
        bonus = 0
        if not duplicate:
            engine = ScoringEngine(score)
            before = engine.total_score
            engine.add_points(30)
            bonus = engine.total_score - before
            score = engine.total_score
            c.execute("INSERT INTO answer_log (ma_nguoi_dung,ma_cau_hoi,dung_sai,diem,thoi_gian) VALUES (?,?,1,?,0)", (user_id, key, bonus))
        completed.add(str(location_name))
        c.execute("UPDATE tien_do_choi SET diem_tri_thuc=?,ma_dia_diem_hien_tai=?,nam_mo_khoa_cao_nhat=MAX(nam_mo_khoa_cao_nhat,?),danh_sach_dia_diem_da_mo=? WHERE ma_nguoi_dung=?", (score, location_id, max_year, json.dumps(sorted(completed), ensure_ascii=False), user_id))
        conn.commit()
        engine = ScoringEngine(score); rank = engine.calculate_rank(score)
        return {"duplicate": duplicate, "bonus": bonus, "total_score": score, "rank": rank, "rank_title": engine.TITLES[rank]}
    except Exception as exc:
        conn.rollback()
        if isinstance(exc, RepositoryError): raise
        raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def list_reviews(user_id: int):
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute("SELECT ma_cau_hoi,location_name,question_text,options_json,correct_index,user_choice,explanation,source_title,source_citation,status,retry_count,reward_awarded FROM review_items WHERE ma_nguoi_dung=? ORDER BY status='PENDING' DESC,updated_at DESC", (user_id,))
        rows = c.fetchall()
        items = []
        for row in rows:
            row["options"] = json.loads(row.pop("options_json") or "[]")
            items.append({"id": str(row.pop("ma_cau_hoi")), **row})
        return items
    finally: conn.close()


def retry_review(user_id: int, question_id: str, choice: int):
    conn = _connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        c = conn.cursor()
        # Cùng thứ tự khóa với submit_answer: tiến độ trước, review sau.
        # Tránh deadlock khi hai request quiz/retry chạy đồng thời.
        c.execute("SELECT diem_tri_thuc FROM tien_do_choi WHERE ma_nguoi_dung=?", (user_id,))
        progress = c.fetchone()
        if not progress:
            raise RepositoryError("Không tìm thấy tiến độ người chơi.")
        c.execute("SELECT correct_index,options_json,reward_awarded FROM review_items WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (user_id, question_id))
        row = c.fetchone()
        if not row: raise RepositoryError("Không tìm thấy câu hỏi ôn tập.")
        options = json.loads(row.get("options_json") or "[]")
        if not 0 <= choice < len(options): raise RepositoryError("Đáp án chọn không hợp lệ.")
        correct = choice == int(row["correct_index"])
        c.execute("UPDATE review_items SET user_choice=?,retry_count=retry_count+1,status=? WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (choice, "MASTERED" if correct else "PENDING", user_id, question_id))
        engine = ScoringEngine(int(progress.get("diem_tri_thuc") or 0))
        reward = 0
        if correct and not bool(row.get("reward_awarded")):
            reward = engine.record_review_reward(question_id)
            c.execute("UPDATE review_items SET reward_awarded=1 WHERE ma_nguoi_dung=? AND ma_cau_hoi=?", (user_id, question_id))
            c.execute("UPDATE tien_do_choi SET diem_tri_thuc=? WHERE ma_nguoi_dung=?", (engine.total_score, user_id))
        conn.commit()
        rank = engine.calculate_rank(engine.total_score)
        return {"is_correct": correct, "points_awarded": reward, "total_score": engine.total_score, "rank": rank, "rank_title": engine.TITLES[rank]}
    except Exception as exc:
        conn.rollback()
        if isinstance(exc, RepositoryError): raise
        raise RepositoryError(str(exc)) from exc
    finally: conn.close()


def teacher_report():
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute("SELECT u.ho_va_ten,p.diem_tri_thuc FROM nguoi_dung u LEFT JOIN tien_do_choi p ON p.ma_nguoi_dung=u.ma_nguoi_dung WHERE LOWER(u.vai_tro) IN ('player','nguoi_choi') ORDER BY p.diem_tri_thuc DESC")
        students = c.fetchall()
        c.execute("SELECT ma_cau_hoi,COUNT(*) AS wrong_count FROM answer_log WHERE dung_sai=0 GROUP BY ma_cau_hoi ORDER BY wrong_count DESC LIMIT 10")
        difficult = c.fetchall()
        return students, difficult
    finally: conn.close()
