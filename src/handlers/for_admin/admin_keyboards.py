from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# клавиатура модерации фото пользователя
def check_photo(user_tg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Разрешить фото ✅',
                              callback_data='close_notification')],
        [InlineKeyboardButton(text='❌ Удалить фото ❌',
                              callback_data=f'delete_user_photo:{user_tg_id}')],
        [InlineKeyboardButton(text='🚷 Заблокировать пользователя 🚷',
                              callback_data=f'send_to_ban:{user_tg_id}')]])


# клавиатура модерации анкеты при жалобе
def get_complaint(user_tg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Пропустить ✅',
                              callback_data='close_notification')],
        [InlineKeyboardButton(text='🚷 Заблокировать пользователя 🚷',
                              callback_data=f'send_to_ban:{user_tg_id}')]])


# АДМИНКА (МЕНЮ)
# Главное меню reply keyboard (для админа)
main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔎 Найти пользователей')],
    [KeyboardButton(text='👋 Мои реакции')],
    [KeyboardButton(text='✏️ Редактировать профиль')],
    [KeyboardButton(text='📬 Оставить отзыв')],
    [KeyboardButton(text='👮‍♂️ Администрирование')]
],
    resize_keyboard=True

)


admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔴 Заблокировать пользователя',
                          callback_data='ban_user')],
    [InlineKeyboardButton(text='🟢 Разблокировать пользователя',
                          callback_data='unban_user')]])

# возврат в главное меню администратора
admin_keyboard_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Назад',
                          callback_data='admin_main_menu')]])
