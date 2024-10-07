import asyncio
import logging
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.modules.loader import loader
from src.database.requests.delete_profile import delete_profile
from config import delete_profile_id

import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'delete_profile')
async def edit_city(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{delete_profile_id}',
            caption=(
                '<b>Вы уверены?</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.delete_profile
    )

    await state.update_data(message_id=edit_message.message_id)


@router.callback_query(F.data == 'confirm_delete')
async def confirm_delete(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_tg_id = callback.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')
    await asyncio.to_thread(delete_profile, user_tg_id)
    await loader(callback.message, 'Удаляю')
    await bot.delete_message(chat_id=user_tg_id, message_id=message_id)
    await state.update_data(user_id=user_tg_id)
    await callback.message.answer(text='Привет!\nЧтобы продолжить, вам нужно:',
                                  reply_markup=kb.regkey)
