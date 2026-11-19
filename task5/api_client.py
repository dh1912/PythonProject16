"""HTTP client chuẩn thư viện Python; không ghi token/mật khẩu vào log."""
from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ApiClientError(RuntimeError):
    pass


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None

    def request(self, method: str, path: str, payload=None, authenticated: bool = True):
        headers = {"Accept": "application/json"}
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if authenticated and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try: message = json.loads(exc.read().decode("utf-8")).get("detail", "Lỗi API")
            except Exception: message = "Lỗi API"
            raise ApiClientError(f"HTTP {exc.code}: {message}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ApiClientError(f"Không kết nối được API: {exc}") from exc

    def get(self, path: str, authenticated: bool = True): return self.request("GET", path, authenticated=authenticated)
    def post(self, path: str, payload=None, authenticated: bool = True): return self.request("POST", path, payload, authenticated)