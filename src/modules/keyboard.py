from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

'''main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🗄 Главное меню', callback_data='main_menu')],
                                             [InlineKeyboardButton(text='🚑 Помощь', callback_data='help')]])'''

regkey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='reg')]])

users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📇 Редактировать профиль',
                          callback_data='my_profile')],
    [InlineKeyboardButton(text='🗃 Найти пользователей', callback_data='users')]
])

about_me = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 Увлечения',
                          callback_data='edit_hobbies'),
     InlineKeyboardButton(text='📷 Фото профиля',
                          callback_data='edit_photo')],
    [InlineKeyboardButton(text='🏷 Имя',
                          callback_data='edit_name'),
     InlineKeyboardButton(text='📆 Возраст',
                          callback_data='edit_age')],
    [InlineKeyboardButton(text='⚧️ Пол',
                          callback_data='edit_gender'),
     InlineKeyboardButton(text='🌆 Город',
                          callback_data='edit_city')],
    [InlineKeyboardButton(text='🗑 Удалить профиль',
                          callback_data='delete_profile')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='main_menu')]])

edit_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📥 Добавить увлечение',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='🚮 Удалить увлечение',
                          callback_data='del_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

no_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📥 Добавить увлечение',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

add_hobby = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📥 Добавить увлечение',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться в профиль', callback_data='my_profile')]])

edit_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='🚮 Удалить фото', callback_data='del_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

edit_no_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_hobbies')]])

gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')]])

gender_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male-search')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female-search')],
    [InlineKeyboardButton(text='Не важно', callback_data='all-search')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='users')]])

edit_gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back_to_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_photo')]])

start_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 Редактировать "Увлечения"',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='↩️ Заполнить позже', callback_data='main_menu')]])


users_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍👩‍👧‍👦 Все пользователи',
                          callback_data='all_users')],
    [InlineKeyboardButton(text='🌆 Поиск людей в вашем городе',
                          callback_data='search_users_in_city')],
    [InlineKeyboardButton(text='🎸 Поиск людей по увлеченям',
                          callback_data='search_users_by_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='main_menu')]])

search_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='users')]])

# Удаление профиля

delete_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='confirm_delete'),
     InlineKeyboardButton(text='Нет', callback_data='my_profile')],

])


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

# Клавиатура удаления хобби


def delete_hobbies_keyboard(hobbies):
    builder = InlineKeyboardBuilder()

    for hobby in hobbies:

        if len(hobby) > 20:
            hobby = hobby[:20]

        button = InlineKeyboardButton(
            text=f'❌ {hobby}', callback_data=f'remove_hobby:{hobby}')
        builder.row(button)  # Добавляем каждую кнопку в отдельной строке

    # Добавляем кнопку "Назад" в отдельной строке
    back_button = InlineKeyboardButton(
        text="Вернуться назад", callback_data="edit_hobbies")
    builder.row(back_button)

    return builder.as_markup()
