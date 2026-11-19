"""Loại bỏ thẻ BrowserFS dead-code mà template Pygbag 0.9.3 trỏ tới URL 404.

Chạy sau pygbag build. Không tải hoặc giả lập BrowserFS; Pygbag maintainer xác nhận
script này không còn được dùng. Chỉ chỉnh HTML build, không đụng source game.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

_BROWSERFS_SCRIPT = re.compile(
    r"\s*<script\s+src=[\"']https://pygame-web\.github\.io/cdn/0\.9\.3//browserfs\.min\.js[\"']\s*>\s*</script>",
    re.IGNORECASE,
)


def patch_build(build_dir: Path) -> bool:
    """Xoá đúng thẻ BrowserFS 0.9.3 nếu template còn sinh ra nó."""
    index = build_dir / "index.html"
    if not index.is_file():
        raise FileNotFoundError(f"Không tìm thấy file build: {index}")
    html = index.read_text(encoding="utf-8")
    patched, count = _BROWSERFS_SCRIPT.subn("", html)
    if count:
        index.write_text(patched, encoding="utf-8", newline="")
    return count > 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path, help="Thư mục Pygbag build/web")
    args = parser.parse_args()
    changed = patch_build(args.build_dir)
    print("Đã bỏ thẻ BrowserFS dead-code." if changed else "Không có thẻ BrowserFS; build đã sạch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())