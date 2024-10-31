from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# клавиатура выбора пола при регистрации
def check_photo(user_tg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Разрешить фото ✅',
                              callback_data='close_notification')],
        [InlineKeyboardButton(text='❌ Удалить фото ❌',
                              callback_data=f'delete_user_photo:{user_tg_id}')],
        [InlineKeyboardButton(text='🚷 Заблокировать пользователя 🚷',
                              callback_data=f'send_to_ban:{user_tg_id}')]])
