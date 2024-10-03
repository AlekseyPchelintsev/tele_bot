from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🗄 Главное меню', callback_data='main_menu')],
                                             [InlineKeyboardButton(text='🚑 Помощь', callback_data='help')]])

regkey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='reg')]])

users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📇 Мой профиль', callback_data='my_profile')],
    [InlineKeyboardButton(text='🗃 Пользователи', callback_data='users')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='back')]])

about_me = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 Редактировать "Увлечения"',
                          callback_data='edit_hobbies')],
    [InlineKeyboardButton(text='📷 Редактировать фото',
                          callback_data='edit_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='main_menu')]])

edit_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📥 Добавить увлечение',
                          callback_data='new_hobbie')],
    [InlineKeyboardButton(text='🚮 Удалить увлечение',
                          callback_data='del_hobbie')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

add_hobby = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📥 Добавить увлечение',
                          callback_data='new_hobbie')],
    [InlineKeyboardButton(text='↩️ Вернуться в профиль', callback_data='my_profile')]])

edit_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='🚮 Удалить фото', callback_data='del_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_hobbies')]])

gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')]])

back_to_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_photo')]])

start_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 Редактировать "Увлечения"',
                          callback_data='my_profile')],
    [InlineKeyboardButton(text='↩️ Заполнить позже', callback_data='back')]])

help_about = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='VK', callback_data='vk',
                          url='https://vk.com/')],
    [InlineKeyboardButton(
        text='YouTuBe', callback_data='youtube', url='https://youtube.com/')],
    [InlineKeyboardButton(
        text='Pinterest', callback_data='pinterest', url='https://pinterest.com/')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='back')]])

users_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗂 Все пользователи',
                          callback_data='all_users')],
    [InlineKeyboardButton(text='🔍 Поиск по увлеченям',
                          callback_data='search_users')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='main_menu')]])

search_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='users')]])

# Создание клавиатуры


class Pagination(CallbackData, prefix='pg'):
    action: str
    page: int
    list_type: str


def paginator(page: int = 0, list_type: str = 'default'):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='◀️', callback_data=Pagination(
            action='prev', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=Pagination(
            action='menu', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=Pagination(
            action='next', page=page, list_type=list_type).pack()),
        # InlineKeyboardButton(text='📖 Посмотреть профиль',callback_data=Pagination(action='user_profile', page=page).pack()),
        width=3
    )
    return builder.as_markup()
