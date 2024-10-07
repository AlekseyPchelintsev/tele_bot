import asyncio
import logging
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from src.modules.loader import loader, attention_message
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.database.requests.gender_change import change_user_gender

import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'edit_gender')
async def change_gender(callback: CallbackQuery):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n'
                '<b>Выберите пол:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.edit_gender
    )


@router.callback_query(F.data.in_(['male', 'female', 'other']))
async def gender_checked(callback: CallbackQuery):

    user_tg_id = callback.from_user.id
    new_gender = callback.data

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.to_thread(change_user_gender, user_tg_id, new_gender)
    await loader(callback.message, 'Вношу изменения')

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n'
                'Данные успешно изменены ✅'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n'
                '<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )


# Удаление лишних сообщений из чата

'''
F.text – regular text message (this has already been done)
F.photo – message with photo
F.video – message with video
F.animation – message with animation (gifs)
F.contact – message sending contact details (very useful for FSM)
F.document – a message with a file (there may also be a photo if it is sent as a document)
F.data – message with CallData (this was processed in the previous article).
'''


@router.message(F.text | F.photo | F.video | F.animation |
                F.contact | F.document | F.sticker)
async def handle_random_message(message: Message):
    await message.delete()
    await attention_message(message, '⚠️ Если вы хотите внести изменения, перейдите '
                            'в раздел <b>"редактировать профиль"</b>')
