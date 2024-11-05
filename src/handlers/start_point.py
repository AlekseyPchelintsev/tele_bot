import asyncio
from aiogram.types import Message, BotCommand
from aiogram.filters import CommandStart, Command
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.database.requests.user_data import check_user
from config import main_menu_logo

# /test
from src.database.requests.admin_requests.ban_and_unban_users import ban_user, unban_user
from src.database.requests.redis_state.redis_get_data import (
    redis_client,
    remove_unbaned_user_from_redis,
    save_users_to_redis
)

import src.handlers.for_admin.admin_keyboards as kb_admin
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    user_id = State()


delete_messages = []
delete_last_message = []


# КОММАНДА /START

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.clear()

    # получение id пользователя
    user_tg_id = message.from_user.id

    # проверка наличия пользователя в бд
    data = await asyncio.to_thread(check_user, user_tg_id)

    # если пользователь есть в бд
    if data:

        # отрисовываю страницу
        await message.answer_photo(
            photo=f'{main_menu_logo}',
            caption=(
                '<b>Главное меню:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.users
        )

    # если пользователя нет в бд
    else:

        # сообщение с предложением зарегистрироваться
        await message.answer(text='Для начала вам нужно:',
                             reply_markup=kb.regkey)


# DEVTOOLS

# Тест функций

'''
@router.message(F.text == '/test')
async def test(message: Message, bot: Bot):

    await bot.set_my_commands([
        BotCommand(command="start", description="Начало")
    ])

    # chat_id = '-4573727711'
    # await bot.send_message(chat_id=chat_id, text='Check: OK')
    # await asyncio.to_thread(save_users_to_redis)

    # Выводим данные из Redis для проверки
    check_delete_users = redis_client.smembers('turn_off_users')
    check_banned_users = redis_client.smembers('banned_users')
    # Преобразуем множество в список и объединяем в строку
    delete_users_list = ', '.join(check_delete_users)
    banned_users_list = ', '.join(check_banned_users)
    await asyncio.to_thread(unban_user, '491366599')
    print(f"Удалившиеся пользователи в Redis: {delete_users_list}")
    print(f"Забаненные пользователи в Redis: {banned_users_list}")
'''

# получение id гурппы(чата)

'''
@router.message(F.text)
async def get_group_id(message: Message):

    await message.answer(f'ID группы: {message.chat.id}')
'''
