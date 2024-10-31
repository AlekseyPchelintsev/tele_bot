
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram import F, Router
from config import gender_search, search_menu
from src.modules.delete_messages import del_last_message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.handlers.for_admin.send_to_ban_list import check_ban_callback

import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Меню "пользователи"


@router.callback_query(F.data == 'users')
@check_ban_callback
async def check_users_menu(callback: CallbackQuery, state: FSMContext):

    # очищаю состояние (контрольно)
    await state.clear()

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{search_menu}',
                caption=(
                    '🔎 <b>Выберите один из вариантов поиска:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users_menu
        )
    except:
        await callback.message.answer_photo(
            photo=f'{search_menu}',
            caption=(
                '🔎 <b>Выберите один из вариантов поиска:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.users_menu
        )


# оработчик колбэков меню поиска


@router.callback_query(F.data.in_(['advanced_search', 'all_users']))
@check_ban_callback
async def search_users_menu(callback: CallbackQuery, state: FSMContext):

    # получаю данные из состояния для следующей загрузки вида поиска
    data = callback.data

    # добавляю в состояниие инфу о выбраном меню чтобы обработать вывод клавиатуры далее
    await state.update_data(type_of_search=data)

    # отрисовка сообщения с клавиатурой
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{gender_search}',
                caption=(
                    '\n\n<b>🔎 Кого ищем?</b>'
                ),
                parse_mode='HTML',
            ),
            reply_markup=kb.gender_search
        )
    except:
        await callback.message.answer_photo(
            photo=f'{gender_search}',
            caption=(
                '\n\n<b>🔎 Кого ищем?</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.gender_search
        )
