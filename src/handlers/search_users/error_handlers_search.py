import asyncio
from aiogram import Router
from aiogram.types import InputMediaPhoto
from config import in_progress
from src.modules.get_self_data import get_user_info
import src.modules.keyboard as kb

router = Router()

delete_messages = []
delete_last_message = []


# неверный формат запроса при поиске по городам
async def wrong_search_city_name(user_tg_id, message_id, bot):

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю название своего города
    city_data = user_info['data'][0][5]

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>В каком городе?</b>'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_in_city(city_data)
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>В каком городе?</b>'
                '\n\n❌ Название города должно содержать <b>только текст</b>, не должно содержать эмодзи '
                'или изображения.'
                '\n\n📌⌨️ Выберите <b>один из вариантов</b> ниже'
                '\n\n📌💬 или пришлите <b>название города</b> в чат'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_in_city(city_data)
    )


# Неверный формат данных при поиске пользователей по хобби
async def wrong_search_hobby_name(user_tg_id, message_id, bot):

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>Какие увлечения?</b>'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.hobbies_search
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>Какие увлечения?</b>'
                '\n\n❌ Название увлечения должно содержать <b>только текст</b>, не должно содержать эмодзи '
                'или изображения.'
                '\n\n📌⌨️ Выберите <b>один из вариантов</b> ниже'
                '\n\n📌💬 или пришлите <b>увлечение</b> в чат'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.hobbies_search
    )
