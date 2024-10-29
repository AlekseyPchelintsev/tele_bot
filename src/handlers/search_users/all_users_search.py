import asyncio
from aiogram.types import InputMediaPhoto
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from src.modules.pagination_logic import load_pagination_start_or_end_data
from src.database.requests.search_users import search_users
from config import gender_search

import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Отображение всех пользователей


async def search_all_users(callback, state, gender_data):

    user_tg_id = callback.from_user.id

    # для передачи в search_users
    city = 'all'
    hobbies = 'all'

    # получаю готовый список пользователей
    data = await asyncio.to_thread(search_users,
                                   user_tg_id,
                                   gender_data,
                                   city,
                                   hobbies)

    # если есть пользователи
    if data:

        total_pages = len(data)

        # если найден всего 1 пользователь
        if total_pages == 1:
            text_info = '\n\n<b>📍 Найден всего 1 пользователь</b>'
        else:
            text_info = ''

        # загрузка пагинации
        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator',
                                                'all_users',
                                                total_pages,
                                                text_info)

        await state.update_data(users_data=data)

    else:

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{gender_search}',
                caption=(
                    '\n\n❌ <b>Пользователи не найдены</b>'
                    '\n\n🔎 Попробуйте изменить параметры поиска.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )
