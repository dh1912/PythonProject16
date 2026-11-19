"""Adapter có API dữ liệu tương thích cơ bản với GameDataService."""
from __future__ import annotations
from typing import Any
import sys
from .api_client import ApiClient, ApiClientError


class ApiGameDataService:
    def __init__(self, api_url: str, timeout: float = 5.0, fallback_service: Any = None):
        self.client = ApiClient(api_url, timeout)
        self.async_auth_enabled = sys.platform == "emscripten"
        self.browser_client = None
        self.fallback_service = fallback_service
        self.current_user = None
        self.locations = getattr(fallback_service, "locations", [])
        self.investigation_data = getattr(fallback_service, "investigation_data", {})
        self.questions = getattr(fallback_service, "questions", {})
        self.is_connected = False
        self.status_message = "API Task 5 chưa kết nối"
        self._progress = {"score": 0, "current_loc_id": 1, "max_year": 1914, "completed": set(), "task4": {}}

    @staticmethod
    def _decode_progress(data):
        return {"score": int(data.get("score", 0)), "current_loc_id": int(data.get("current_loc_id", 1)),
                "max_year": int(data.get("max_year", 1914)), "completed": set(data.get("completed", [])), "task4": data.get("task4", {})}

    def _auth(self, endpoint, payload):
        try:
            data = self.client.post(endpoint, payload, authenticated=False)
            self.client.token = data["access_token"]
            self.current_user = data["user"]
            self._progress = self._decode_progress(data.get("progress", {}))
            self.is_connected = True
            return True, self.current_user, self._progress
        except (ApiClientError, KeyError, ValueError, TypeError) as exc:
            self.status_message = str(exc)
            return False, None, self.status_message

    def login(self, username, password):
        ok, user, progress = self._auth("/auth/login", {"username": username, "password": password})
        if ok:
            try: self._progress = self._decode_progress(self.client.get("/progress/me").get("data", {}))
            except ApiClientError as exc: return False, None, str(exc)
        return ok, user, self._progress if ok else progress

    authenticate = login

    async def authenticate_async(self, username: str, password: str, fullname: str | None = None):
        """Đăng nhập/đăng ký browser; không gọi urllib hoặc mở kết nối SQL."""
        from .browser_client import BrowserApiClient
        if self.browser_client is None:
            self.browser_client = BrowserApiClient(self.client.base_url, self.client.timeout)
        endpoint = "/auth/register" if fullname is not None else "/auth/login"
        payload = {"username": username, "password": password}
        if fullname is not None:
            payload["fullname"] = fullname
        try:
            data = await self.browser_client.request("POST", endpoint, payload, authenticated=False)
            token = data["access_token"]
            user = data["user"]
            progress = self._decode_progress(data.get("progress", {}))
            self.browser_client.token = token
            # Nạp review trước khi áp dụng phiên, tránh callback phiên gọi HTTP đồng bộ.
            remote = await self.browser_client.request("GET", "/review/me")
            self._browser_reviews = remote.get("items", [])
            self.client.token = token
            self.current_user = user
            self._progress = progress
            self.is_connected = True
            return True, user, progress
        except (ApiClientError, KeyError, TypeError, ValueError) as exc:
            self.logout()
            self.status_message = str(exc)
            return False, None, self.status_message

    def register(self, username, password, fullname):
        return self._auth("/auth/register", {"username": username, "password": password, "fullname": fullname})

    def load_user_progress(self, user_id):
        self._progress = self._decode_progress(self.client.get("/progress/me").get("data", {})); return self._progress

    def sync_user_progress(self, user_id, current_loc_id, max_year, score, completed_set):
        try:
            response = self.client.post("/progress/save", {"current_loc_id": current_loc_id, "max_year": max_year, "completed": list(completed_set)})
            self._progress.update(current_loc_id=current_loc_id, max_year=max_year, completed=set(completed_set)); return True, response
        except ApiClientError as exc: return False, str(exc)

    def load_task4_progress(self, user_id):
        if self.async_auth_enabled:
            return self._progress.get("task4", {})
        return self.load_user_progress(user_id).get("task4", {})

    def sync_task4_progress(self, user_id, location_id, clue_ids, quiz_attempts):
        task4 = dict(self._progress.get("task4", {})); task4[str(location_id)] = {"clue_ids": sorted(set(clue_ids)), "quiz_attempts": int(quiz_attempts)}
        try:
            result = self.client.post("/progress/save", {"current_loc_id": self._progress["current_loc_id"], "max_year": self._progress["max_year"], "completed": list(self._progress["completed"]), "task4": task4})
            self._progress["task4"] = task4; return True, result
        except ApiClientError as exc: return False, str(exc)

    def load_game_data(self):
        # Chỉ đọc cache đã có; API client không tự mở kết nối MySQL desktop.
        return {"locations": self.locations, "investigation_data": self.investigation_data, "questions": self.questions, "is_connected": False, "status_message": self.status_message}

    def get_locations_from_db(self): return self.locations
    def logout(self):
        self.client.token = None
        if self.browser_client:
            self.browser_client.token = None
        self._browser_reviews = []
        self.current_user = None
        self.is_connected = False
        self._progress = {"score": 0, "current_loc_id": 1, "max_year": 1914, "completed": set(), "task4": {}}
        return True
    def submit_answer(self, question_id, choice_index, elapsed_seconds):
        return self.client.post("/quiz/submit", {"ma_cau_hoi": str(question_id), "dap_an_chon": int(choice_index), "so_giay": float(elapsed_seconds)})

    def complete_quest(self, location_id, location_name, max_year):
        result = self.client.post("/quest/complete", {"ma_dia_diem": int(location_id), "ten_dia_diem": str(location_name), "nam_mo_khoa": int(max_year)})
        self._progress["score"] = int(result.get("total_score", self._progress["score"]))
        return result

    def get_review_items(self):
        if self.async_auth_enabled:
            return list(getattr(self, "_browser_reviews", []))
        return self.client.get("/review/me").get("items", [])
    def retry_review(self, question_id, choice_index):
        return self.client.post("/review/retry", {"ma_cau_hoi": str(question_id), "dap_an_chon": int(choice_index)})
    def get_leaderboard(self): return self.client.get("/leaderboard", authenticated=False).get("leaderboard", [])