import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from src.handlers.start_point import router as command_start_router
from src.handlers.registration import router as registration_router
from src.handlers.main_menu import router as main_menu_router
from src.handlers.my_profile import router as my_profile_router
from src.handlers.edit_hobbies import router as edit_hobbies_router
from src.handlers.edit_photo import router as edit_photo_router
from src.handlers.edit_city import router as edit_city_router
from src.handlers.pagination import router as pagination_router
from src.handlers.delete_your_page import router as delete_page_router
from src.handlers.edit_name import router as edit_name
from src.handlers.edit_age import router as edit_age
from src.handlers.edit_gender import router as edit_gender
from src.handlers.like_reactions_menu import router as like_reactions
from src.database.models import create_tables

bot = Bot(token=TOKEN)


async def main():
    await asyncio.to_thread(create_tables)
    dp = Dispatcher()
    dp.include_router(command_start_router)
    dp.include_router(registration_router)
    dp.include_router(main_menu_router)
    dp.include_router(my_profile_router)
    dp.include_router(edit_hobbies_router)
    dp.include_router(edit_photo_router)
    dp.include_router(edit_city_router)
    dp.include_router(pagination_router)
    dp.include_router(like_reactions)
    dp.include_router(delete_page_router)
    dp.include_router(edit_name)
    dp.include_router(edit_age)
    dp.include_router(edit_gender)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
