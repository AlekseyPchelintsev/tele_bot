import asyncio
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.database.requests.user_data import check_user
from src.handlers.for_admin.send_to_ban_list import check_ban_message
from config import main_menu_logo
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    user_id = State()


delete_messages = []
delete_last_message = []


# КОММАНДА /START

@router.message(CommandStart())
@check_ban_message
async def start(message: Message, state: FSMContext):

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
    chat_id = '-4573727711'
    await bot.send_message(chat_id=chat_id, text='Check: OK')
'''

# получение id гурппы(чата)

'''
@router.message(F.text)
async def get_group_id(message: Message):

    await message.answer(f'ID группы: {message.chat.id}')
'''
