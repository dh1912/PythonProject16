"""Bảo đảm staging không đóng gói dữ liệu người chơi và script patch có tính lặp."""
from pathlib import Path
import tempfile
import pytest
from task5.build_web import stage_project
from task5.patch_pygbag_build import patch_build


def test_build_refuses_source_directory():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        with pytest.raises(ValueError):
            stage_project(root, root / "task5")


def test_staging_allowlist_excludes_secrets_profiles_and_server():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        for directory in ("scenes", "services", "task4", "task5", "data", "assets/fonts", "task5/server", "data/reviews"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        for name in ("config.py", "main.py", "main_web.py", "bando.jpg", "left_axis.png", "data/db_queries.py", "assets/fonts/NotoSans.ttf", ".env", "data/reviews/player_1.json", "task5/server/auth.py"):
            (root / name).write_text("test", encoding="utf-8")
        destination = stage_project(root, root / "build" / "web-source")
        assert not (destination / ".env").exists()
        assert not (destination / "data/reviews").exists()
        assert not (destination / "task5/server").exists()
        assert (destination / "main.py").is_file()
        stage_project(root, destination)


def test_browserfs_patch_is_idempotent():
    with tempfile.TemporaryDirectory() as folder:
        index = Path(folder) / "index.html"
        index.write_text('<script src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"></script><canvas></canvas>', encoding="utf-8")
        assert patch_build(Path(folder))
        assert not patch_build(Path(folder))
        assert index.read_text(encoding="utf-8") == "<canvas></canvas>"