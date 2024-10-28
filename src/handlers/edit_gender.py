import asyncio
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from src.modules.notifications import loader
from src.modules.get_self_data import get_user_info
from src.database.requests.gender_change import change_user_gender

import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'edit_gender')
async def change_gender(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']
    self_gender = user_info['gender']

    # отрисовка страницы
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш пол:</b> {self_gender}'
                '\n\n<b>Выберите один из вариантов:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.edit_gender
    )


@router.callback_query(F.data.in_(['male', 'female', 'other']))
async def gender_changed(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # получаю данные пола из колбэка
    new_gender = callback.data

    # изменение данных в бд
    await asyncio.to_thread(change_user_gender, user_tg_id, new_gender)

    # плучаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_photo = self_data[0][1]
    self_name = self_data[0][0]
    self_age = self_data[0][4]
    self_city = self_data[0][5]
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']
    # учеба/работа
    employment = user_info['employment']
    employment_info = user_info['employment_info']

    # отрисовка страницы с учетом внесенных изменений
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_photo}',
            caption=(
                f'{self_gender}'  # пол
                f' • {self_name}'  # имя
                f' • {self_age}'  # возраст
                f' • {self_city}'  # город
                f'\n► <b>{employment}:</b> {employment_info}'
                f'\n► <b>Увлечения:</b> {self_hobbies}'
                f'\n► <b>О себе:</b> {about_me}'
                '\n\nДанные успешно изменены ✅'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )
