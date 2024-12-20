import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN, ADMIN_IDs

# обработка /start, регистрация, галвное меню, мой профиль
from src.handlers.start_point import router as command_start_router
from src.handlers.registration import router as registration_router
from src.handlers.main_menu import router as main_menu_router
from src.handlers.my_profile import router as my_profile_router

# обработка редактирования своей нкеты и ее удаление
from src.handlers.edit_profile.edit_hobbies import router as edit_hobbies_router
from src.handlers.edit_profile.edit_photo import router as edit_photo_router
from src.handlers.edit_profile.edit_city import router as edit_city_router
from src.handlers.edit_profile.edit_name import router as edit_name
from src.handlers.edit_profile.edit_age import router as edit_age
from src.handlers.edit_profile.edit_gender import router as edit_gender
from src.handlers.edit_profile.edit_about_me import router as edit_about_me
from src.handlers.edit_profile.edit_employment import router as edit_employment
from src.handlers.edit_profile.turn_off_page import router as delete_page_router

# обработка поиска пользователей
from src.handlers.search_users.search_users_menu import router as search_users_menu
from src.handlers.search_users.all_users_search import router as search_all_users
from src.handlers.search_users.gender_search import router as search_gender
from src.handlers.search_users.city_search import router as search_city
from src.handlers.search_users.hobby_search import router as search_hobby
from src.handlers.search_users.pagination_search import router as search_pagination

# обработка меню "мои реакции"
from src.handlers.reactions_menu.hide_users import router as reactions_hide_users
from src.handlers.reactions_menu.incoming_reactions import router as reactions_incoming
from src.handlers.reactions_menu.main_menu_reactions import router as reactions_main_menu
from src.handlers.reactions_menu.match_reactions import router as reactions_match
from src.handlers.reactions_menu.my_reactions import router as reactions_my
from src.handlers.reactions_menu.notice_reaction import router as reactions_notice
from src.handlers.reactions_menu.pagination_reactions import router as reactions_pagination

# middlewares
from src.modules.middlewares import (TurnOffUsersMiddleware,
                                     BannedUsersMiddleware,
                                     AdminCheckMiddleware,
                                     set_admin_commands_menu)

# проверка redis
from src.database.requests.redis_state.check_redis_state import start_background_tasks

# админка
from src.handlers.for_admin.check_users_photos import router as admin_check_photo
from src.handlers.for_admin.ban_and_unban_user import router as ban_users
from src.handlers.for_admin.feedback_from_users import router as feedback_from_users
from src.handlers.for_admin.admin_menu_handlers import router as admin_main_menu

# создание таблиц в бд (если не созданы)
from src.database.models import create_tables


bot = Bot(token=TOKEN)


async def main():
    await asyncio.to_thread(create_tables)

    # добавляю администраторам дополнительные команды в меню
    await set_admin_commands_menu(bot, ADMIN_IDs)

    dp = Dispatcher()

    # фоновый процесс проверки состояния redis
    await start_background_tasks(dp)

    # мидлвари для отключенных анкет
    dp.message.middleware(TurnOffUsersMiddleware())
    dp.callback_query.middleware(TurnOffUsersMiddleware())

    # мидлварь для забаненых
    dp.update.middleware(BannedUsersMiddleware())

    # мидлварь для админов
    dp.message.middleware(AdminCheckMiddleware())

    # администрирование
    dp.include_router(admin_check_photo)
    dp.include_router(ban_users)
    dp.include_router(feedback_from_users)
    dp.include_router(admin_main_menu)

    # обработка меню
    dp.include_router(command_start_router)
    dp.include_router(registration_router)
    dp.include_router(main_menu_router)
    dp.include_router(my_profile_router)

    # редактриование профиля
    dp.include_router(edit_hobbies_router)
    dp.include_router(edit_photo_router)
    dp.include_router(edit_city_router)
    dp.include_router(edit_name)
    dp.include_router(edit_age)
    dp.include_router(edit_gender)
    dp.include_router(edit_about_me)
    dp.include_router(edit_employment)
    dp.include_router(delete_page_router)

    # система поиска пользователей
    dp.include_router(search_users_menu)
    dp.include_router(search_all_users)
    dp.include_router(search_gender)
    dp.include_router(search_city)
    dp.include_router(search_hobby)
    dp.include_router(search_pagination)

    # меню "мои реакции"
    dp.include_router(reactions_hide_users)
    dp.include_router(reactions_incoming)
    dp.include_router(reactions_main_menu)
    dp.include_router(reactions_match)
    dp.include_router(reactions_my)
    dp.include_router(reactions_notice)
    dp.include_router(reactions_pagination)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
