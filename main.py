import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
import asyncio
from hendlers import router as hendlers_router


load_dotenv()
TOKEN = os.getenv("token")


dp = Dispatcher()
dp.include_routers(
    hendlers_router #роутер
)


async def main():
    bot = Bot(TOKEN)
     #инициализация бд
    await dp.start_polling(bot) 
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен!")