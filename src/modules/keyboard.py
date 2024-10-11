from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

'''main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🗄 Главное меню', callback_data='main_menu')],
                                             [InlineKeyboardButton(text='🚑 Помощь', callback_data='help')]])'''

# Регистрация

regkey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='reg')]])

gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')]])

# Главное меню

users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗃 Найти пользователей',
                          callback_data='users')],
    [InlineKeyboardButton(text='❤️ Мои реакции',
                          callback_data='all_reactions')],
    [InlineKeyboardButton(text='📇 Редактировать профиль',
                          callback_data='my_profile')]
])

# Реакции

reactions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⤴️ Исходящие запросы',
                          callback_data='my_reactions')],
    [InlineKeyboardButton(text='⤵️ Входящие запросы',
                          callback_data='incoming_reactions_list')],
    [InlineKeyboardButton(text='🗂 Мои контакты',
                          callback_data='match_reactions_list')],
    [InlineKeyboardButton(text='🚫 Заблокированные пользователи',
                          callback_data='ignore_list')],
    [InlineKeyboardButton(text='↩️ Вернуться назад',
                          callback_data='main_menu')]
])

# хводящий запрос на добавление в контакты


def incoming_request_reaction(current_user_id):

    request_reaction = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Ответить 👋',
                              callback_data=f'accept_request:{current_user_id}'),
         InlineKeyboardButton(text='Отложить 💤',
                              callback_data='accept_late')]
    ])
    return request_reaction


error_add_to_contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Понятно 👌',
                          callback_data='main_menu')]
])

# Если нет реакций

back_reactions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔎 Поиск пользователей',
                          callback_data='users')],
    [InlineKeyboardButton(text='↩️ Вернуться к реакциям',
                          callback_data='all_reactions')]
])

# Взаимные реакции


def match_reactions(nickname):
    match_users_reactions = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✉️ Перейти в чат',
                              url=f'https://t.me/{nickname}')],
        [InlineKeyboardButton(text='↩️ В главное меню',
                              callback_data='main_menu')]
    ])
    return match_users_reactions

# Меню редактирования профиля


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
     InlineKeyboardButton(text='🏘 Город',
                          callback_data='edit_city')],
    [InlineKeyboardButton(text='🗑 Удалить профиль',
                          callback_data='delete_profile')],
    [InlineKeyboardButton(text='↩️ Главное меню', callback_data='main_menu')]])

# Редактирование хобби

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

back_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_hobbies')]])

# Клавиатура удаления хобби


def delete_hobbies_keyboard(hobbies):
    builder = InlineKeyboardBuilder()

    for hobby in hobbies:

        if len(hobby) > 20:
            hobby = hobby[:20]

        button = InlineKeyboardButton(
            text=f'🚫 {hobby}', callback_data=f'remove_hobby:{hobby}')
        builder.row(button)  # Добавляем каждую кнопку в отдельной строке

    # Добавляем кнопку "Назад" в отдельной строке
    back_button = InlineKeyboardButton(
        text="Вернуться назад", callback_data="edit_hobbies")
    builder.row(back_button)

    return builder.as_markup()

# Редактирование фото профиля


edit_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='🚮 Удалить фото', callback_data='del_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

edit_no_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

back_to_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_photo')]])

# Общий возврат в мой профиль

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])

# Редактирование пола

edit_gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


start_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 Редактировать "Увлечения"',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='↩️ Заполнить позже', callback_data='main_menu')]])

# Поиск пользователей

users_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍👩‍👧‍👦 Все пользователи',
                          callback_data='all_users')],
    [InlineKeyboardButton(text='🌆 Поиск людей в вашем городе',
                          callback_data='search_users_in_city')],
    [InlineKeyboardButton(text='🎸 Поиск людей по увлеченям',
                          callback_data='search_users_by_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='main_menu')]])

# Возврат из поиска

search_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='users')]])

# Выбор пола для поиска

gender_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male-search')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female-search')],
    [InlineKeyboardButton(text='Не важно', callback_data='all-search')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='users')]])

# Удаление профиля

delete_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='confirm_delete'),
     InlineKeyboardButton(text='Нет', callback_data='my_profile')],

])


# Клавиатура пагинации поиска пользователей


class Pagination(CallbackData, prefix='pg'):
    action: str
    page: int
    list_type: str


def paginator(page: int = 0, list_type: str = 'default', action: str = 'like'):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='◀️', callback_data=Pagination(
            action='prev', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=Pagination(
            action='menu', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=Pagination(
            action='next', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='Отправить реакцию 👋', callback_data=Pagination(
            action='like', page=page, list_type=list_type).pack()),
        width=3
    )
    return builder.as_markup()


# Клавиатуры пагинации просмотра реакций


class PaginationLikes(CallbackData, prefix='pg_likes'):
    action: str
    page: int
    list_type: str


def paginator_likes(page: int = 0, list_type: str = 'default', action: str = 'in_reactions_dislike'):
    builder_likes = InlineKeyboardBuilder()
    builder_likes.row(
        InlineKeyboardButton(text='◀️', callback_data=PaginationLikes(
            action='prev_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=PaginationLikes(
            action='next_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='Отменить реакцию 🚫', callback_data=PaginationLikes(
            action='in_reactions_dislike', page=page, list_type=list_type).pack()),
        width=3
    )
    return builder_likes.as_markup()


def incoming_reactions(page: int = 0, list_type: str = 'default', action: str = 'in_reactions_like'):
    builder_incoming_likes = InlineKeyboardBuilder()
    builder_incoming_likes.row(
        InlineKeyboardButton(text='◀️', callback_data=PaginationLikes(
            action='prev_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=PaginationLikes(
            action='next_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='Ответить 👋', callback_data=PaginationLikes(
            action='in_reactions_like', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='Не интересно 🚫', callback_data=PaginationLikes(
            action='delete_incoming', page=page, list_type=list_type).pack()),
        width=3
    )
    return builder_incoming_likes.as_markup()


def match_reactions_pagination(page: int = 0, list_type: str = '', nickname: str = '', action: str = 'start_chat'):
    builder_incoming_likes = InlineKeyboardBuilder()
    builder_incoming_likes.row(
        InlineKeyboardButton(text='◀️', callback_data=PaginationLikes(
            action='prev_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=PaginationLikes(
            action='next_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='✉️ Чат',
                             url=f'https://t.me/{nickname}'),
        InlineKeyboardButton(text='🚫 Удалить', callback_data=PaginationLikes(
            action='delete_contact', page=page, list_type=list_type).pack()),
        width=3
    )

    return builder_incoming_likes.as_markup()


def ignored_users_pagination(page: int = 0, list_type: str = '', action: str = 'start_dialog'):
    builder_incoming_likes = InlineKeyboardBuilder()
    builder_incoming_likes.row(
        InlineKeyboardButton(text='◀️', callback_data=PaginationLikes(
            action='prev_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='↩️ Назад', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='▶️', callback_data=PaginationLikes(
            action='next_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='♻️ Вернуть в поиск', callback_data=PaginationLikes(
            action='remove_from_ignore', page=page, list_type=list_type).pack()),
        width=3
    )

    return builder_incoming_likes.as_markup()
