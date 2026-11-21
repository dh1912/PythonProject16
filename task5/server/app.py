"""FastAPI cho đăng nhập, chấm quiz và lưu tiến độ Task 5."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import TASK5_ALLOWED_ORIGINS, TASK5_WEB_BUILD_DIR
from task5.scoring_system import ScoringEngine
from . import repository
from .auth import get_current_user, issue_token, normalize_role, password_hash, password_matches, require_role

app = FastAPI(title="Task 5 - Game Lịch sử Việt Nam", version="1.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=TASK5_ALLOWED_ORIGINS, allow_credentials=True,
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def disable_web_build_cache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/web/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


class Register(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)
    fullname: str = Field(min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        # bcrypt giới hạn byte UTF-8, không phải số ký tự Unicode.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu vượt quá 72 byte UTF-8.")
        return value


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu vượt quá 72 byte UTF-8.")
        return value


class Quiz(BaseModel):
    ma_cau_hoi: str = Field(min_length=1, max_length=100)
    dap_an_chon: int = Field(ge=0, le=3)
    so_giay: float = Field(ge=0.25, le=3600, allow_inf_nan=False)

    @field_validator("so_giay")
    @classmethod
    def reasonable_time(cls, value: float) -> float:
        if 0 < value < 0.25:
            raise ValueError("Thời gian nhỏ bất thường.")
        return value


class Progress(BaseModel):
    current_loc_id: int = Field(ge=0)
    max_year: int = Field(ge=1911, le=1975)
    completed: list[str] = Field(default_factory=list, max_length=100)
    task4: dict[str, Any] = Field(default_factory=dict)


class QuestComplete(BaseModel):
    ma_dia_diem: int = Field(ge=1)
    ten_dia_diem: str = Field(min_length=1, max_length=255)
    nam_mo_khoa: int = Field(ge=1911, le=1975)


class ReviewRetry(BaseModel):
    ma_cau_hoi: str = Field(min_length=1, max_length=100)
    dap_an_chon: int = Field(ge=0, le=3)


def _public(user: dict[str, Any]):
    return {"ma_nguoi_dung": int(user["ma_nguoi_dung"]), "ten_dang_nhap": user.get("ten_dang_nhap", ""),
            "ho_va_ten": user.get("ho_va_ten", ""), "vai_tro": normalize_role(user.get("vai_tro"))}


@app.get("/api/health")
def health(): return {"status": "healthy", "service": "task5"}


@app.get("/game/questions")
def game_questions():
    """Cấp bộ câu hỏi hiện hành có ID; chấm điểm vẫn luôn truy vấn DB server."""
    from data import db_queries
    from services.game_data_service import transform_deduction_questions, transform_locations, transform_investigation_data
    events, event_message = db_queries.fetch_raw_su_kien()
    questions, question_message = db_queries.fetch_raw_cau_hoi()
    if events is None or questions is None:
        raise HTTPException(503, "Chưa tải được bộ câu hỏi từ CSDL.")
    locations, _ = db_queries.fetch_raw_dia_diem()
    characters, _ = db_queries.fetch_raw_nhan_vat()
    clues, _ = db_queries.fetch_raw_manh_moi()
    if any(rows is None for rows in (locations, characters, clues)):
        raise HTTPException(503, "Chưa tải được dữ liệu điều tra.")
    return {"questions": transform_deduction_questions(events, questions),
            "locations": transform_locations(locations, events),
            "investigation_data": transform_investigation_data(locations, events, characters, clues)}


@app.get("/", include_in_schema=False)
def root_page():
    """Chuyển vào game khi có build; nếu chưa có thì hiện hướng dẫn thay vì JSON 404."""
    if _WEB.is_dir() and (_WEB / "index.html").is_file():
        return RedirectResponse(url="/web/", status_code=307)
    return HTMLResponse(
        "<!doctype html><html lang='vi'><meta charset='utf-8'>"
        "<title>Task 5 API</title><h1>Task 5 API đang chạy</h1>"
        "<p>Bản game web chưa được mount. Hãy cấu hình WEB_BUILD_DIR trỏ tới thư mục build/web đã xác minh.</p>"
        "<p><a href='/api/health'>Kiểm tra API</a> | <a href='/docs'>Tài liệu API</a></p>"
        "</html>", status_code=200
    )


@app.post("/auth/register", status_code=201)
def register(body: Register):
    try: user = repository.create_user(body.username, password_hash(body.password), body.fullname)
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể đăng ký.") from exc
    if user is None: raise HTTPException(409, "Tên đăng nhập đã tồn tại.")
    return {"access_token": issue_token(user), "token_type": "bearer", "user": _public(user),
            "progress": {"score": 0, "current_loc_id": 1, "max_year": 1914, "completed": [], "task4": {}}}


@app.post("/auth/login")
@limiter.limit("5/minute")
def login(request: Request, body: Login):
    try:
        user = repository.get_user(body.username)
        if not user: raise HTTPException(401, "Tên đăng nhập hoặc mật khẩu không đúng.")
        stored = repository.get_hash(int(user["ma_nguoi_dung"]))
        if stored:
            valid = password_matches(body.password, stored)
        else:
            # Di chuyển legacy: kiểm tra mật khẩu cũ rồi chỉ ghi hash mới, không ghi đè mật khẩu.
            valid = repository.authenticate_legacy(body.username, body.password) is not None
            if valid: repository.set_hash(int(user["ma_nguoi_dung"]), password_hash(body.password))
        if not valid: raise HTTPException(401, "Tên đăng nhập hoặc mật khẩu không đúng.")
        progress = repository.load_progress(int(user["ma_nguoi_dung"]))
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể truy cập CSDL.") from exc
    user["vai_tro"] = normalize_role(user.get("vai_tro"))
    return {"access_token": issue_token(user), "token_type": "bearer", "user": _public(user), "progress": progress}


@app.post("/quiz/submit")
@limiter.limit("30/minute")
def quiz_submit(request: Request, body: Quiz, user=Depends(get_current_user)):
    try: return repository.submit_answer(user["ma_nguoi_dung"], body.ma_cau_hoi, body.dap_an_chon, body.so_giay)
    except repository.RepositoryError as exc: raise HTTPException(404 if "Không tìm thấy" in str(exc) else 400, str(exc)) from exc


@app.get("/progress/me")
def progress_me(user=Depends(get_current_user)):
    try: return {"data": repository.load_progress(user["ma_nguoi_dung"])}
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể tải tiến độ.") from exc


@app.post("/progress/save")
def progress_save(body: Progress, user=Depends(get_current_user)):
    try: repository.save_progress(user["ma_nguoi_dung"], body.current_loc_id, body.max_year, body.completed, body.task4)
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể lưu tiến độ.") from exc
    return {"success": True}


@app.post("/quest/complete")
def quest_complete(body: QuestComplete, user=Depends(get_current_user)):
    try: return repository.complete_quest(user["ma_nguoi_dung"], body.ma_dia_diem, body.ten_dia_diem, body.nam_mo_khoa)
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể lưu quest.") from exc


@app.get("/review/me")
def review_me(user=Depends(get_current_user)):
    try: return {"items": repository.list_reviews(user["ma_nguoi_dung"])}
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể tải ôn tập.") from exc


@app.post("/review/retry")
def review_retry(body: ReviewRetry, user=Depends(get_current_user)):
    try: return repository.retry_review(user["ma_nguoi_dung"], body.ma_cau_hoi, body.dap_an_chon)
    except repository.RepositoryError as exc: raise HTTPException(400, str(exc)) from exc


@app.get("/review/summary")
def review_summary(user=Depends(get_current_user)):
    try: items = repository.list_reviews(user["ma_nguoi_dung"])
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể tải tổng kết ôn tập.") from exc
    total = len(items); mastered = sum(x.get("status") == "MASTERED" for x in items)
    return {"total": total, "pending": total-mastered, "mastered": mastered,
            "mastered_rate": mastered * 100 / total if total else 0}


@app.get("/leaderboard")
def leaderboard():
    try: rows = repository.leaderboard(10)
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể tải Bảng Vàng.") from exc
    return {"leaderboard": [{"display_name": r.get("display_name", ""), "score": int(r.get("score") or 0)} for r in rows]}


@app.get("/teacher", response_class=HTMLResponse)
def teacher_page(user=Depends(require_role("giao_vien", "quan_tri"))):
    return """<!doctype html><html lang='vi'><meta charset='utf-8'><h1>Báo cáo học sinh</h1><pre id='r'>Đang tải…</pre><script>fetch('/teacher/report',{headers:{Authorization:'Bearer '+sessionStorage.getItem('task5_token')}}).then(r=>r.json()).then(x=>document.querySelector('#r').textContent=JSON.stringify(x,null,2)).catch(e=>document.querySelector('#r').textContent=e)</script></html>"""


@app.get("/teacher/login", response_class=HTMLResponse)
def teacher_login_page():
    """Trang công khai chỉ chứa form; báo cáo thật vẫn yêu cầu JWT và vai trò."""
    return """<!doctype html><html lang="vi"><meta charset="utf-8">
    <title>Đăng nhập giáo viên</title><h1>Báo cáo giáo viên</h1>
    <form id="login"><label>Tài khoản <input id="username" autocomplete="username" required></label>
    <label>Mật khẩu <input id="password" type="password" autocomplete="current-password" required></label>
    <button>Đăng nhập</button></form><p id="error"></p><pre id="report"></pre>
    <button id="logout" hidden>Đăng xuất</button><script>
    let token = null;
    document.querySelector('#login').onsubmit = async e => {
      e.preventDefault(); document.querySelector('#error').textContent = '';
      try {
        const response = await fetch('/auth/login', {method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({username:document.querySelector('#username').value,password:document.querySelector('#password').value})});
        document.querySelector('#password').value = '';
        const auth = await response.json(); if(!response.ok) throw Error(auth.detail || 'Đăng nhập thất bại');
        token = auth.access_token;
        const report = await fetch('/teacher/report', {headers:{Authorization:'Bearer '+token}});
        const data = await report.json(); if(!report.ok) throw Error(data.detail || 'Không đủ quyền');
        document.querySelector('#report').textContent = JSON.stringify(data,null,2);
        document.querySelector('#login').hidden = true; document.querySelector('#logout').hidden = false;
      } catch(error) { token=null; document.querySelector('#error').textContent=error.message; }
    };
    document.querySelector('#logout').onclick=()=>{token=null;document.querySelector('#report').textContent='';
      document.querySelector('#login').hidden=false;document.querySelector('#logout').hidden=true;};
    </script></html>"""


@app.get("/teacher/report")
def teacher_report(user=Depends(require_role("giao_vien", "quan_tri"))):
    try: students, missed = repository.teacher_report()
    except repository.RepositoryError as exc: raise HTTPException(503, "Không thể tải báo cáo.") from exc
    safe = []
    for row in students:
        score = int(row.get("diem_tri_thuc") or 0); engine = ScoringEngine(score); rank = engine.calculate_rank(score)
        safe.append({"display_name": row.get("ho_va_ten", ""), "score": score, "rank": rank, "rank_title": engine.TITLES[rank]})
    return {"students": safe, "most_missed": [{"question_id": r["ma_cau_hoi"], "wrong_count": r["wrong_count"]} for r in missed]}


# Cùng origin: phục vụ build web nếu đã được tạo bởi Pygbag.
from pathlib import Path
from fastapi.staticfiles import StaticFiles
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if TASK5_WEB_BUILD_DIR:
    _WEB = Path(TASK5_WEB_BUILD_DIR).resolve()
else:
    # Ưu tiên build chuẩn, sau đó tự tìm build staging local để tránh API root báo 404.
    _WEB_CANDIDATES = (
        _PROJECT_ROOT / "build" / "web-source" / "build" / "web",
        _PROJECT_ROOT / "build" / "web",
        _PROJECT_ROOT / ".web-staging" / "build" / "web",
    )
    _WEB = next((candidate for candidate in _WEB_CANDIDATES if (candidate / "index.html").is_file()), _WEB_CANDIDATES[0])
if _WEB.is_dir():
    app.mount("/web", StaticFiles(directory=str(_WEB), html=True), name="game-web")