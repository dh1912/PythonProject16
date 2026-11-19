"""Entry point riêng cho Pygbag; dùng chung Game và async loop của desktop."""
import asyncio
import sys

from main import Game


async def main():
    # Trên browser, bật API cùng origin; URL thật do biến môi trường lúc build/deploy.
    if sys.platform == "emscripten":
        import config
        config.TASK5_SERVER_ENABLED = True
    game = Game()
    await game.run_async()


if __name__ == "__main__":
    asyncio.run(main())