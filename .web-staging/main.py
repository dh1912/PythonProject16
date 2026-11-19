import asyncio
import sys
import traceback
from pathlib import Path
import pygame
import config

_FONT_FILE = Path(__file__).resolve().parent / "assets" / "fonts" / "Arial.ttf"
pygame.init()

def _bundled_font(name, size, bold=False, italic=False):
    font = pygame.font.Font(str(_FONT_FILE), size)
    font.set_bold(bool(bold))
    font.set_italic(bool(italic))
    return font

pygame.font.SysFont = _bundled_font
print("WEB_DIAG: entrypoint imported; platform=", sys.platform)
from game_desktop import Game
print("WEB_DIAG: game module imported")

async def main():
    print("WEB_DIAG: entering async main")
    if sys.platform == "emscripten":
        config.TASK5_SERVER_ENABLED = True
        config.TASK5_API_URL = ""
    try:
        game = Game()
        print("WEB_DIAG: Game constructed; scene=", game.scene)
        await game.run_async()
    except Exception:
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())
