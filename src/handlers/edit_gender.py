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
            ),
            parse_mode='HTML'
        )
    )

    # изменение данных в бд
    await asyncio.to_thread(change_user_gender, user_tg_id, new_gender)
    await loader(callback.message, 'Вношу изменения')

    # плучаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']

    # отрисовка страницы с учетом внесенных изменений
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш пол:</b> {self_gender}'
                '\n\nДанные успешно изменены ✅'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'<b>Имя:</b> {self_data[0][0]}'
                f'\n<b>Возраст:</b> {self_data[0][4]}'
                f'\n<b>Пол:</b> {self_gender}'
                f'\n<b>Город:</b> {self_data[0][5]}'
                f'\n\n<b>Увлечения:</b> {self_hobbies}'
                f'\n\n<b>О себе:</b> {about_me}'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )
