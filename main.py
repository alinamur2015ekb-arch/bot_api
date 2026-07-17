import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
import asyncio
from aiohttp import web
from hendlers import router as hendlers_router

load_dotenv()
TOKEN = os.getenv("token")
if not TOKEN:
    raise RuntimeError("Не задан токен бота (переменная token в .env)")

dp = Dispatcher()
dp.include_routers(hendlers_router)

async def run_polling(bot):
    await dp.start_polling(bot)

async def create_web_server():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")
    # Держим сервер живым
    while True:
        await asyncio.sleep(3600)

async def main():
    bot = Bot(TOKEN)
    # Запускаем polling и веб‑сервер параллельно
    await asyncio.gather(
        run_polling(bot),
        create_web_server(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")
