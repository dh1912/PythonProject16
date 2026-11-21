"""Tạo font dùng được trên browser (font đóng gói) và desktop (SysFont dự phòng)."""
from pathlib import Path
import sys
import pygame


def task5_font(size: int, bold: bool = False):
    font_path = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "NotoSans.ttf"
    if sys.platform == "emscripten" and font_path.is_file():
        font = pygame.font.Font(str(font_path), size)
        font.set_bold(bold)
        return font
    return pygame.font.SysFont("segoeui,arial,timesnewroman", size, bold=bold)