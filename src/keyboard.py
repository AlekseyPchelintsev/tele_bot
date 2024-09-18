from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🗄 Главное меню')],
                                     [KeyboardButton(text='🚑 Помощь')], 
                                     [KeyboardButton(text='>>>hash(float("inf"))')]],
                           resize_keyboard=True,
                           one_time_keyboard=True,)

regkey = ReplyKeyboardMarkup(keyboard=[
  [KeyboardButton(text='Зарегистрироваться')]],
                  one_time_keyboard=True,
                  resize_keyboard=True)

users = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text='📇 Мой профиль', callback_data='my_profile')],
  [InlineKeyboardButton(text='🗃 Пользователи', callback_data='users')],
  [InlineKeyboardButton(text='Вернуться назад', callback_data='back')]])

help_about = InlineKeyboardMarkup(inline_keyboard=[
  [InlineKeyboardButton(text='VK', callback_data='vk', url='https://vk.com/')],
  [InlineKeyboardButton(text='YouTuBe', callback_data='youtube', url='https://youtube.com/')],
  [InlineKeyboardButton(text='Pinterest', callback_data='pinterest', url='https://pinterest.com/')],
  [InlineKeyboardButton(text='Вернуться назад', callback_data='back')]])

#Создание клавиатуры
class Pagination(CallbackData, prefix='pg'):
  action: str
  page: int
  
def paginator(page: int=0):
  builder = InlineKeyboardBuilder()
  builder.row(
    InlineKeyboardButton(text='◀️',callback_data=Pagination(action='prev', page=page).pack()),
    InlineKeyboardButton(text='Меню',callback_data=Pagination(action='menu', page=page).pack()),
    InlineKeyboardButton(text='▶️',callback_data=Pagination(action='next', page=page).pack()),
    width=3
  )
  return builder.as_markup()