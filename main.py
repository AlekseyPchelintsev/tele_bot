import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from src.handlers import router
from src.database.models import asy_main

bot = Bot(token=TOKEN)


async def main():
    await asy_main()
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
