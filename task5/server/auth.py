"""Tiện ích bcrypt/JWT và kiểm tra quyền API Task 5."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import TASK5_JWT_SECRET

_bearer = HTTPBearer(auto_error=False)


def normalize_role(value: Any) -> str:
    role = str(value or "player").strip().casefold()
    if role in {"admin", "quan_tri", "quản_trị", "administrator"}:
        return "quan_tri"
    if role in {"teacher", "giao_vien", "giáo_viên"}:
        return "giao_vien"
    return "nguoi_choi"


def _secret() -> str:
    if len(TASK5_JWT_SECRET) < 32:
        raise RuntimeError("JWT_SECRET cần tối thiểu 32 ký tự.")
    return TASK5_JWT_SECRET


def issue_token(user: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user["ma_nguoi_dung"]), "ma_nguoi_dung": int(user["ma_nguoi_dung"]),
                       "vai_tro": normalize_role(user.get("vai_tro")), "iat": now,
                       "exp": now + timedelta(hours=1)}, _secret(), algorithm="HS256")


def password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def password_matches(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Cần đăng nhập.")
    try:
        claim = jwt.decode(credentials.credentials, _secret(), algorithms=["HS256"])
        from .repository import get_user_by_id
        user = get_user_by_id(int(claim["ma_nguoi_dung"]))
        if not user:
            raise HTTPException(401, "Tài khoản không còn tồn tại.")
        return {"ma_nguoi_dung": int(user["ma_nguoi_dung"]), "vai_tro": normalize_role(user.get("vai_tro"))}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(401, "JWT không hợp lệ hoặc đã hết hạn.") from exc


def require_role(*roles: str):
    allowed = {normalize_role(role) for role in roles}

    def dependency(user: dict[str, Any] = Depends(get_current_user)):
        if user["vai_tro"] not in allowed:
            raise HTTPException(403, "Bạn không có quyền truy cập.")
        return user
    return dependency