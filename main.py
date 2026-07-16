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

async def on_startup(app):
    asyncio.create_task(dp.start_polling(bot))

async def handle(request):
    return web.Response(text="Bot is running")
    
load_dotenv()
TOKEN = os.getenv("token")

dp = Dispatcher()
dp.include_routers(
    hendlers_router #роутер
)

async def main():
    bot = Bot(TOKEN)
    await dp.start_polling(bot) 
    asyncio.create_task(pinger())
    app = web.Application()
    app.on_startup.append(on_startup)
    app.router.add_get('/', handle)
    port = int(os.environ.get("PORT", 10000))
    return web.run_app(app, host='0.0.0.0', port=port)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")
