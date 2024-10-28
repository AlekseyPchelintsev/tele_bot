import asyncio
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.database.requests.user_data import check_user
from config import main_menu_logo
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    user_id = State()


delete_messages = []
delete_last_message = []


# КОММАНДА /START

@router.message(CommandStart())
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
async def test(message: Message):
    user_tg_id = message.from_user.id
    hobby = 'цц'
    test = await asyncio.to_thread(check_hobby, hobby)
    await message.answer(f'{test}')
'''
