"""Adapter có API dữ liệu tương thích cơ bản với GameDataService."""
from __future__ import annotations
from typing import Any
import sys
import asyncio
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
        self.pending_operations = set()
        self.network_errors = []
        self._session_generation = 0
        self._write_lock = None
        self.save_state = 'confirmed'
        self.save_error = None
        self._save_revision = 0
        self._question_sessions = {}
        self._question_starts = {}
        self._question_expiry = {}

    def prepare_question(self, question_id):
        """Gọi khi câu hỏi xuất hiện, không tạo đồng hồ mới tại thời điểm nộp bài."""
        qid = str(question_id)
        import time
        if qid in self._question_sessions and time.monotonic() >= self._question_expiry.get(qid, float('inf')):
            self._question_sessions.pop(qid, None)
            self._question_expiry.pop(qid, None)
        if qid in self._question_sessions or qid in self._question_starts:
            return
        if not self.async_auth_enabled:
            self._question_sessions[qid] = self.client.post('/quiz/start', {'ma_cau_hoi':qid})['session_id']
            return
        generation = self._session_generation
        async def start():
            try:
                result = await self.request_async('POST','/quiz/start',{'ma_cau_hoi':qid})
                if generation == self._session_generation:
                    self._question_sessions[qid] = result['session_id']
                    # TTL server -> monotonic local, không phụ thuộc đồng hồ máy người chơi.
                    self._question_expiry[qid] = time.monotonic()+max(0, result.get('remaining_seconds',3600))
            finally:
                if generation == self._session_generation:
                    self._question_starts.pop(qid, None)
        self._question_starts[qid] = self._schedule(start())

    async def request_async(self, method, path, payload=None, authenticated=True):
        """Transport dùng chung cho mọi hành động browser, không gọi urllib."""
        from .browser_client import BrowserApiClient
        if self.browser_client is None:
            self.browser_client = BrowserApiClient(self.client.base_url, self.client.timeout)
            self.browser_client.token = self.client.token
        generation = self._session_generation
        if method.upper() == "POST":
            # Giữ thứ tự save manh mối -> hoàn thành quest trong cùng phiên browser.
            if self._write_lock is None:
                self._write_lock = asyncio.Lock()
            async with self._write_lock:
                if generation != self._session_generation:
                    raise ApiClientError('Phiên đăng nhập đã thay đổi.')
                result = await self.browser_client.request(method, path, payload, authenticated)
                if generation != self._session_generation:
                    raise ApiClientError('Phiên đăng nhập đã thay đổi.')
                return result
        result = await self.browser_client.request(method, path, payload, authenticated)
        if generation != self._session_generation:
            raise ApiClientError('Phiên đăng nhập đã thay đổi.')
        return result

    def _schedule(self, coroutine):
        generation = self._session_generation
        task = asyncio.create_task(coroutine)
        self.pending_operations.add(task)
        def finished(completed):
            self.pending_operations.discard(completed)
            if not completed.cancelled():
                error = completed.exception()
                if error and generation == self._session_generation:
                    self.network_errors.append(str(error))
        task.add_done_callback(finished)
        return task

    async def submit_answer_async(self, question_id, choice_index, elapsed_seconds):
        generation = self._session_generation
        qid = str(question_id)
        if qid in self._question_starts:
            await self._question_starts[qid]
        payload = {"ma_cau_hoi": qid, "dap_an_chon": int(choice_index), "so_giay": float(elapsed_seconds)}
        if qid in self._question_sessions:
            payload['session_id'] = self._question_sessions[qid]
        try:
            result = await self.request_async("POST", "/quiz/submit", payload)
        except ApiClientError as exc:
            if 'hết hạn' in str(exc):
                self._question_sessions.pop(qid, None)
                self._question_expiry.pop(qid, None)
                self.prepare_question(qid)
                raise ApiClientError('Phiên câu hỏi hết hạn. Đang mở phiên mới; hãy đọc lại câu và thử lại.') from exc
            await self.reconcile_progress(generation)
            raise
        if generation != self._session_generation:
            raise ApiClientError("Phiên đăng nhập đã thay đổi.")
        self._progress["score"] = int(result["total_score"])
        if not result.get('correct'):
            self._question_sessions.pop(qid, None)
        return result

    async def reconcile_progress(self, generation=None):
        """Chỉ đọc sau kết quả không chắc chắn, không tự cấp thưởng hay gửi lại."""
        generation = self._session_generation if generation is None else generation
        if generation != self._session_generation:
            return
        self.save_state = 'reconciling'
        try:
            result = await self.request_async('GET','/progress/me')
            if generation == self._session_generation:
                self._progress = self._decode_progress(result['data'])
        finally:
            if generation == self._session_generation:
                self.save_state = 'failed'

    async def retry_review_async(self, question_id, choice_index):
        generation = self._session_generation
        try:
            result = await self.request_async("POST", "/review/retry", {"ma_cau_hoi": str(question_id), "dap_an_chon": int(choice_index)})
        except ApiClientError:
            await self.reconcile_progress(generation)
            raise
        if generation != self._session_generation:
            raise ApiClientError("Phiên đăng nhập đã thay đổi.")
        self._progress["score"] = int(result["total_score"])
        return result

    async def get_leaderboard_async(self):
        return (await self.request_async("GET", "/leaderboard", authenticated=False)).get("leaderboard", [])

    async def refresh_reviews_async(self):
        generation = self._session_generation
        result = await self.request_async("GET", "/review/me")
        if generation != self._session_generation:
            raise ApiClientError("Phiên đăng nhập đã thay đổi.")
        self._browser_reviews = result.get("items", [])
        return list(self._browser_reviews)

    async def load_notebook_async(self):
        return (await self.request_async('GET','/notebook/clues')).get('items',[])

    async def collect_clue_async(self, location_id: int, clue_id: str, official_title: str):
        generation = self._session_generation
        try:
            result = await self.request_async('POST', '/clues/collect', {
                'ma_dia_diem': int(location_id), 'ma_manh_moi': str(clue_id), 'tu_lieu_chon': str(official_title)})
        except ApiClientError:
            await self.reconcile_progress(generation)
            raise
        if generation != self._session_generation:
            raise ApiClientError('Phiên đăng nhập đã thay đổi.')
        task = dict(self._progress.get('task4', {}))
        key = str(location_id)
        old = task.get(key, {})
        task[key] = {'clue_ids': sorted(set(old.get('clue_ids', [])) | set(result['collected'])),
                     'quiz_attempts': int(old.get('quiz_attempts', 0))}
        self._progress['task4'] = task
        return result

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
        if self.async_auth_enabled:
            return dict(self._progress)
        self._progress = self._decode_progress(self.client.get("/progress/me").get("data", {})); return self._progress

    def sync_user_progress(self, user_id, current_loc_id, max_year, score, completed_set):
        if self.async_auth_enabled:
            payload = {"current_loc_id": int(current_loc_id), "max_year": int(max_year), "completed": list(completed_set)}
            self._queue_save(payload)
            return True, "Đã xếp hàng lưu; chưa xác nhận máy chủ."
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
        if self.async_auth_enabled:
            payload = {"current_loc_id": self._progress["current_loc_id"], "max_year": self._progress["max_year"], "completed": list(self._progress["completed"]), "task4": task4}
            self._queue_save(payload)
            return True, "Đã xếp hàng lưu nhiệm vụ."
        try:
            result = self.client.post("/progress/save", {"current_loc_id": self._progress["current_loc_id"], "max_year": self._progress["max_year"], "completed": list(self._progress["completed"]), "task4": task4})
            self._progress["task4"] = task4; return True, result
        except ApiClientError as exc: return False, str(exc)

    def load_game_data(self):
        if not self.async_auth_enabled:
            result = self.client.get('/game/content', authenticated=False)
            self.locations = result['locations']
            self.investigation_data = result['investigation_data']
            self.questions = result['questions']
            self.notebook_items = result['notebook']
            return result
        # Browser nạp bằng fetch từ main_web; không bao giờ mở DB local.
        return {"locations": self.locations, "investigation_data": self.investigation_data, "questions": self.questions, "is_connected": False, "status_message": self.status_message}

    def get_locations_from_db(self): return self.locations

    def _queue_save(self, payload):
        """Không sửa cache đã xác nhận bằng trạng thái dự đoán của client."""
        self._save_revision += 1
        revision = self._save_revision
        generation = self._session_generation
        self.save_state = 'queued'
        self.save_error = None

        async def persist():
            if generation != self._session_generation:
                return
            self.save_state = 'pending'
            try:
                await self.request_async('POST', '/progress/save', payload)
                result = await self.request_async('GET', '/progress/me')
                if generation == self._session_generation and revision == self._save_revision:
                    self._progress = self._decode_progress(result['data'])
                    self.save_state = 'confirmed'
            except Exception as exc:
                if generation != self._session_generation:
                    return
                # Timeout có thể xảy ra sau COMMIT: đọc lại thay vì tự cộng/thưởng hoặc gửi lặp.
                if revision == self._save_revision:
                    self.save_state = 'reconciling'
                try:
                    result = await self.request_async('GET', '/progress/me')
                    if generation == self._session_generation and revision == self._save_revision:
                        self._progress = self._decode_progress(result['data'])
                except Exception:
                    pass
                if generation == self._session_generation and revision == self._save_revision:
                    self.save_state = 'failed'
                    self.save_error = str(exc)
                raise
        return self._schedule(persist())

    def logout(self):
        self._session_generation += 1
        self._save_revision += 1
        self._question_sessions.clear()
        self._question_starts.clear()
        self._question_expiry.clear()
        self.save_state = 'confirmed'
        self.save_error = None
        self.network_errors.clear()
        for task in tuple(self.pending_operations):
            task.cancel()
        self.client.token = None
        if self.browser_client:
            self.browser_client.token = None
        self._browser_reviews = []
        self.current_user = None
        self.is_connected = False
        self._progress = {"score": 0, "current_loc_id": 1, "max_year": 1914, "completed": set(), "task4": {}}
        return True
    def submit_answer(self, question_id, choice_index, elapsed_seconds):
        if self.async_auth_enabled:
            raise ApiClientError("Browser phải dùng submit_answer_async.")
        payload = {"ma_cau_hoi": str(question_id), "dap_an_chon": int(choice_index), "so_giay": float(elapsed_seconds)}
        if str(question_id) in self._question_sessions:
            payload['session_id'] = self._question_sessions[str(question_id)]
        result = self.client.post("/quiz/submit", payload)
        if not result.get('correct'):
            self._question_sessions.pop(str(question_id), None)
        return result

    def complete_quest(self, location_id, location_name, max_year):
        if self.async_auth_enabled:
            raise ApiClientError('Browser cần chờ complete_quest_async.')
        result = self.client.post("/quest/complete", {"ma_dia_diem": int(location_id), "ten_dia_diem": str(location_name), "nam_mo_khoa": int(max_year)})
        self._progress["score"] = int(result.get("total_score", self._progress["score"]))
        return result

    async def complete_quest_async(self, location_id, location_name, max_year):
        generation = self._session_generation
        if self.pending_operations:
            await asyncio.gather(*tuple(self.pending_operations))
        try:
            result = await self.request_async('POST', '/quest/complete', {'ma_dia_diem':int(location_id), 'ten_dia_diem':str(location_name), 'nam_mo_khoa':int(max_year)})
        except ApiClientError:
            await self.reconcile_progress(generation)
            raise
        if generation != self._session_generation:
            raise ApiClientError('Phiên đăng nhập đã thay đổi.')
        self._progress['score'] = int(result['total_score'])
        self._progress['completed'].add(str(location_name))
        return result

    def get_review_items(self):
        if self.async_auth_enabled:
            return list(getattr(self, "_browser_reviews", []))
        return self.client.get("/review/me").get("items", [])
    def retry_review(self, question_id, choice_index):
        if self.async_auth_enabled:
            raise ApiClientError("Browser phải dùng retry_review_async.")
        return self.client.post("/review/retry", {"ma_cau_hoi": str(question_id), "dap_an_chon": int(choice_index)})
    def get_leaderboard(self):
        if self.async_auth_enabled:
            raise ApiClientError("Browser phải dùng get_leaderboard_async.")
        return self.client.get("/leaderboard", authenticated=False).get("leaderboard", [])