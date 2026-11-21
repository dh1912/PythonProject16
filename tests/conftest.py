"""Mọi test mặc định dùng SQLite tạm, không được chạm game.db người dùng."""
import os
import tempfile
from pathlib import Path

_temporary = tempfile.TemporaryDirectory(prefix='task5-pytest-')
os.environ['SQLITE_DB_PATH'] = str(Path(_temporary.name) / 'tests.db')
os.environ.setdefault('JWT_SECRET', 'isolated-test-secret-at-least-32-characters')