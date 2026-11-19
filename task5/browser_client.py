"""Transport JSON bất đồng bộ cho Pygbag, dùng fetch và platform.jsiter.

Không log payload hoặc token. Giới hạn thời gian bằng AbortController, lỗi HTTP
và lỗi mạng đều trả kết quả kết thúc thay vì chờ vô hạn trong generator.
"""
from __future__ import annotations
import json
from .api_client import ApiClientError

_BRIDGE = r"""
window.task5Fetch = function* (url, optionsText, timeoutMs) {
    let finished = false;
    let result = null;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const options = JSON.parse(optionsText);
    options.signal = controller.signal;
    fetch(url, options).then(async response => {
        result = {status: response.status, text: await response.text()};
    }).catch(error => {
        result = {status: 0, text: '', error: String(error)};
    }).finally(() => {
        clearTimeout(timer);
        finished = true;
    });
    while (!finished) yield;
    yield JSON.stringify(result);
};
"""


class BrowserApiClient:
    def __init__(self, base_url: str, timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None
        self.initialized = False

    async def request(self, method: str, path: str, payload=None, authenticated: bool = True):
        import platform
        if not self.initialized:
            platform.window.eval(_BRIDGE)
            self.initialized = True
        headers = {"Accept": "application/json"}
        options = {"method": method, "headers": headers, "credentials": "same-origin"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
            options["body"] = json.dumps(payload, ensure_ascii=False)
        if authenticated and self.token:
            headers["Authorization"] = "Bearer " + self.token
        result = json.loads(await platform.jsiter(platform.window.task5Fetch(
            self.base_url + path, json.dumps(options), int(self.timeout * 1000))))
        return self.decode(result)

    @staticmethod
    def decode(result: dict):
        if not result.get("status"):
            raise ApiClientError("Không kết nối được API hoặc đã hết thời gian chờ.")
        try:
            body = json.loads(result.get("text", ""))
        except (ValueError, TypeError) as exc:
            raise ApiClientError("API không trả JSON hợp lệ.") from exc
        if not 200 <= result["status"] < 300:
            raise ApiClientError(f"HTTP {result['status']}: {body.get('detail', 'Lỗi API')}")
        return body