"""Kiểm thử giải mã kết quả fetch, không yêu cầu mạng hoặc WebAssembly."""
import pytest
from task5.browser_client import BrowserApiClient
from task5.api_client import ApiClientError


def test_browser_decode_success():
    assert BrowserApiClient.decode({"status": 200, "text": '{"score":30}'}) == {"score": 30}


@pytest.mark.parametrize("result", [
    {"status": 0, "error": "AbortError"},
    {"status": 503, "text": '{"detail":"Unavailable"}'},
    {"status": 200, "text": "<html>not json</html>"},
])
def test_browser_decode_failures_are_explicit(result):
    with pytest.raises(ApiClientError):
        BrowserApiClient.decode(result)