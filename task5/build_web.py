"""Tạo staging sạch theo allowlist; không đóng gói secret/hồ sơ/SQL server."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import ast


def redact_browser_answers(source: str) -> str:
    """Bỏ đáp án fallback và tuple timeline khỏi bản WASM, không sửa source desktop/server."""
    class Redact(ast.NodeTransformer):
        def visit_Dict(self, node):
            self.generic_visit(node)
            kept = [(k, v) for k, v in zip(node.keys, node.values)
                    if not isinstance(k, ast.Constant) or k.value not in {'answer', 'correct_index', 'explanation'}]
            node.keys, node.values = [k for k, _ in kept], [v for _, v in kept]
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id == '_questions' and len(node.args) == 2:
                for row in getattr(node.args[1], 'elts', []):
                    if isinstance(row, ast.Tuple) and len(row.elts) in (5, 6):
                        row.elts[2] = ast.Constant(None)
                        row.elts[-2] = ast.Constant('')
            return node
    return ast.unparse(ast.fix_missing_locations(Redact().visit(ast.parse(source)))) + '\n'


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
    for folder in ("scenes", "services", "task3", "task4", "task5"):
        for source in (root / folder).glob("*.py"):
            if folder == 'task5' and source.name.startswith(('check_', 'ci_', 'build_', 'patch_', 'test_')):
                continue
            target = destination / folder / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for filename in ("config.py", "bando.jpg", "left_axis.png"):
        shutil.copy2(root / filename, destination / filename)
    shutil.copy2(root / "main.py", destination / "game_desktop.py")
    shutil.copy2(root / "main_web.py", destination / "main.py")
    for relative in ('services/game_data_service.py', 'scenes/deduction_scene.py', 'task4/timeline_data.py'):
        source = destination / relative
        if source.is_file():
            source.write_text(redact_browser_answers(source.read_text(encoding='utf-8')), encoding='utf-8')
    font = root / "assets" / "fonts" / "NotoSans.ttf"
    if not font.is_file():
        raise FileNotFoundError("Thiếu font; cần font tiếng Việt được phép phân phối.")
    target_font = destination / "assets" / "fonts" / font.name
    target_font.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(font, target_font)
    license_file = root / 'assets/fonts/OFL.txt'
    if license_file.is_file():
        shutil.copy2(license_file, target_font.parent / 'OFL.txt')
    # Chỉ cần helper import cho cache desktop; không copy dữ liệu tài khoản.
    data_dir = destination / "data"
    data_dir.mkdir()
    # Browser chỉ import các tên helper để dựng cache; mọi gọi DB đều bị chặn.
    (data_dir / 'db_queries.py').write_text('''"""Web stub: không có SQLite/database/secret trong WebAssembly."""
def _unavailable(*args, **kwargs):
    return None, "Browser phải dùng API"
fetch_raw_dia_diem = fetch_raw_su_kien = fetch_raw_nhan_vat = fetch_raw_manh_moi = fetch_raw_cau_hoi = _unavailable
authenticate_user = register_user = fetch_user_progress = save_user_progress = fetch_task4_progress = save_task4_progress = get_db_connection = _unavailable
''', encoding='utf-8')
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