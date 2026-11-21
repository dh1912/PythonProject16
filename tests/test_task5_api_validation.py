"""Test validation/API thuần, chặn mọi kết nối DB trong các trường hợp kiểm tra."""
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from task5.server.app import app, Quiz, Register, Login
from task5.api_game_data_service import ApiGameDataService
from pydantic import ValidationError


class TestValidation(unittest.TestCase):
    def test_reject_zero_negative_nan_and_infinite_time(self):
        for seconds in (0, -1, 0.01, float("nan"), float("inf")):
            with self.subTest(seconds=seconds), self.assertRaises(ValidationError):
                Quiz(ma_cau_hoi="1", dap_an_chon=1, so_giay=seconds)
        self.assertEqual(Quiz(ma_cau_hoi="1", dap_an_chon=1, so_giay=0.25).so_giay, 0.25)

    def test_bcrypt_limit_is_bytes_not_characters(self):
        for model in (Register, Login):
            with self.subTest(model=model), self.assertRaises(ValidationError):
                model(username="test", password="ế" * 30, fullname="Test")

    def test_teacher_rejects_missing_token_without_database(self):
        with patch("task5.server.repository._connect", side_effect=AssertionError("Không được kết nối DB")):
            with TestClient(app) as client:
                self.assertEqual(client.get("/teacher").status_code, 401)

    def test_adapter_cache_never_calls_sql_fallback(self):
        fallback = Mock(locations=[], investigation_data={}, questions={})
        service = ApiGameDataService("http://localhost", fallback_service=fallback)
        service.async_auth_enabled = True
        service.load_game_data()
        fallback.load_game_data.assert_not_called()
        service.logout()
        self.assertEqual(service._progress["score"], 0)


if __name__ == "__main__":
    unittest.main()