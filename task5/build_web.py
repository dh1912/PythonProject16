"""Tạo staging sạch theo allowlist; không đóng gói secret/hồ sơ/SQL server."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def stage_project(root: Path, destination: Path) -> Path:
    """Staging chỉ được nằm trong build, tránh xóa nhầm source hay môi trường ảo."""
    root = root.resolve()
    destination = destination.resolve()
    if destination.parent != root / "build" or destination.name != "web-source":
        raise ValueError("Chỉ cho phép staging tại build/web-source của dự án.")
    destination.mkdir(parents=True, exist_ok=True)
    # Không ghi đè/xóa thư mục lạ chưa có dấu nhận diện của script.
    marker = destination / ".task5-generated"
    if any(destination.iterdir()) and not marker.is_file():
        raise ValueError("Thư mục staging chưa có dấu nhận diện; không xóa dữ liệu.")
    if marker.is_file():
        shutil.rmtree(destination)
        destination.mkdir()
    marker.write_text("Task 5 staging sinh tự động", encoding="utf-8")
    for folder in ("scenes", "services", "task4", "task5"):
        for source in (root / folder).glob("*.py"):
            target = destination / folder / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for filename in ("config.py", "bando.jpg", "left_axis.png"):
        shutil.copy2(root / filename, destination / filename)
    shutil.copy2(root / "main.py", destination / "game_desktop.py")
    shutil.copy2(root / "main_web.py", destination / "main.py")
    font = root / "assets" / "fonts" / "Arial.ttf"
    if not font.is_file():
        raise FileNotFoundError("Thiếu font; cần font tiếng Việt được phép phân phối.")
    target_font = destination / "assets" / "fonts" / font.name
    target_font.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(font, target_font)
    # Chỉ cần helper import cho cache desktop; không copy dữ liệu tài khoản.
    data_dir = destination / "data"
    data_dir.mkdir()
    shutil.copy2(root / "data" / "db_queries.py", data_dir / "db_queries.py")
    return destination


def main() -> int:
    # PowerShell có thể dùng cp1252 kể cả khi file nguồn là UTF-8.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    staging = stage_project(root, root / "build" / "web-source")
    if args.stage_only:
        print(staging)
        return 0
    subprocess.run([sys.executable, "-X", "utf8", "-m", "pygbag", "--build", "--ume_block", "0", str(staging)], check=True)
    from task5.patch_pygbag_build import patch_build
    patch_build(staging / "build" / "web")
    print(f"Đã đóng gói tại {staging / 'build' / 'web'}; chưa xác nhận runtime browser.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())