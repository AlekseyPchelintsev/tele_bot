import asyncio
import logging
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_last_message
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'main_menu')
async def open_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users
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
                f'<b>Увлечения:</b> {hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.users
        )
