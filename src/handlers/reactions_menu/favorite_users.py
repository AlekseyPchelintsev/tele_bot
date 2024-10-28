import asyncio

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_messages, del_last_message
from config import in_progress
import src.modules.keyboard as kb


router = Router()


# добавление пользователя в раздел "избранное"
@router.callback_query(F.data == 'favorite_users')
async def add_to_favorite_users(callback: CallbackQuery):

    await callback.message.edit_media(media=InputMediaPhoto(
        media=in_progress,
        caption='⚠️ <b>Раздел в процессе разработки</b>',
        parse_mode='HTML'),
        reply_markup=kb.error_add_to_contacts_from_reactions_menu
    )
