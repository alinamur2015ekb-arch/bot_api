import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
import asyncio
from hendlers import router as hendlers_router
from aiohttp import web

async def pinger():
    """Функция, которая сама пингует сайт бота, чтобы он не спал"""
    await asyncio.sleep(10)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get('https://telegramm-bot-rpin.onrender.com') as response:
                    print(f"Пинг выполнен! Статус: {response.status}")
            except Exception as e:
                print(f"Ошибка пинга: {e}")
            await asyncio.sleep(600)

async def health(request):
    return web.Response(text="OK")

def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
    
load_dotenv()
TOKEN = os.getenv("token")

dp = Dispatcher()
dp.include_routers(
    hendlers_router #роутер
)

async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot) 
    asyncio.create_task(dp.start_polling(bot))
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
     runner = web.AppRunner(web.Application())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    print(f"Web server started on port {port}")
    asyncio.create_task(pinger())
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")
