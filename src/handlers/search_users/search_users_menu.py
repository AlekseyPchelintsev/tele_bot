
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info

import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Меню "пользователи"


@router.callback_query(F.data == 'users')
async def check_users_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (контрольно)
    await state.clear()

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные
    self_data = user_info['data']

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '🔎 <b>Выберите один из вариантов поиска:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users_menu
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                '🔎 <b>Выберите один из вариантов поиска:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.users_menu
        )


# оработчик колбэков меню поиска


@router.callback_query(F.data.in_(['advanced_search', 'all_users']))
async def search_users_menu(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = callback.data

    # добавляю в состояниие инфу о выбраном меню чтобы обработать вывод клавиатуры далее
    await state.update_data(type_of_search=data)

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']

    # отрисовка сообщения с клавиатурой
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '\n\n<b>🔎 Кого ищем?</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                '\n\n<b>🔎 Кого ищем?</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.gender_search
        )
