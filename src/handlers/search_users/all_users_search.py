import asyncio
from aiogram.types import InputMediaPhoto
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from src.modules.pagination_logic import load_pagination_start_or_end_data
from src.modules.notifications import loader
from src.database.requests.search_users import search_users
from src.modules.get_self_data import get_user_info

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

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']

    # для передачи в search_users
    city = 'all'
    hobbies = 'all'

    try:

        # получаю готовый список пользователей
        data = await asyncio.to_thread(search_users,
                                       user_tg_id,
                                       gender_data,
                                       city,
                                       hobbies)

    except Exception as e:
        print(f'SHOW ALL USERS ERROR: {e}')

    if data:
        total_pages = len(data)
        await loader(callback.message, 'Секунду, загружаю 🤔')
        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator',
                                                'all_users',
                                                total_pages)

        await state.update_data(users_data=data)

    else:

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        '\n\n❌ <b>Пользователи не найдены</b>'
                        '\n\n🔎 Попробуйте изменить параметры поиска.'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.gender_search
            ))
