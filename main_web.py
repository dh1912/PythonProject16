"""Entry point riêng cho Pygbag; dùng chung Game và async loop của desktop."""
import asyncio
import sys

import importlib


async def main():
    # Trên browser, bật API cùng origin; URL thật do biến môi trường lúc build/deploy.
    if sys.platform == "emscripten":
        import config
        config.TASK5_SERVER_ENABLED = True
        # API cùng origin, không trỏ browser của người chơi về localhost mặc định.
        import platform
        config.TASK5_API_URL = str(platform.window.location.origin)
        import pygame
        from pathlib import Path
        font_file = Path(__file__).resolve().parent / "assets" / "fonts" / "Arial.ttf"

        def bundled_font(name, size, bold=False, italic=False):
            """Tương thích scene desktop mà không sửa source các task khác."""
            font = pygame.font.Font(str(font_file), size)
            font.set_bold(bold)
            font.set_italic(italic)
            return font

        pygame.font.SysFont = bundled_font
    # Trong staging, main.py là entry point này; game được đổi tên riêng.
    module_name = "game_desktop" if (__import__("pathlib").Path(__file__).parent / "game_desktop.py").is_file() else "main"
    Game = importlib.import_module(module_name).Game
    game = Game()
    if sys.platform == "emscripten":
        # Tải trong task riêng: màn login tiếp tục vẽ khi DB/API chậm hoặc lỗi.
        async def load_questions():
            try:
                response = await game.data_service.request_async("GET", "/game/questions", authenticated=False)
                questions = response["questions"]
                game.data_service.questions = questions
                game.game_data["questions"] = questions
                game.deduction_scene.questions_bank = questions
            except Exception as exc:
                game.notify(f"Chưa tải được câu hỏi server: {exc}")
        asyncio.create_task(load_questions())
    if sys.platform == "emscripten":
        # Đánh dấu sau frame game thật, không dùng canvas loader làm bằng chứng.
        game.step()
        platform.window.task5GameReady = True
    await game.run_async()


if __name__ == "__main__":
    asyncio.run(main())