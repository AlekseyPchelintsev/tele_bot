from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Меню')], 
                                     [KeyboardButton(text='Test button')]],
                           resize_keyboard=True,
                           one_time_keyboard=True,
                           input_field_placeholder='Select action...')

regkey = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text='Зарегистрироваться', 
                        callback_data='registration')]])

users = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text='Мой профиль', callback_data='my_profile')],
  [InlineKeyboardButton(text='Пользователи', callback_data='users')]])