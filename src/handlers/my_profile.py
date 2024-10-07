import asyncio
import logging
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_messages, del_last_message
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
import src.modules.keyboard as kb


delete_messages = []
delete_last_message = []

router = Router()

# Меню "мой профиль"


@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await state.clear()
    await del_messages(callback.message.chat.id, delete_messages)
    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    await asyncio.sleep(.5)
    try:
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
    except:
        try:
            await del_last_message(callback.message)
        except:
            pass
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n'
                '<b>Редактировать:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.about_me
        )
