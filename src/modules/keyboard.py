from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from src.database.requests.hobbies_data import get_hobby_id_by_hobby_name


# кнопка региистрации
regkey = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Зарегистрироваться', callback_data='reg')]])


# клавиатура выбора пола при регистрации
gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')]])


# пропустить добавление фото профиля
late_upload_photo_to_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Загрузить позже',
                          callback_data='late_load_photo')]])


# клавиатура выбора работа/учебы при регистрации
check_job_or_study = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💼 Работаю', callback_data='work')],
    [InlineKeyboardButton(text='📚 Учусь', callback_data='study')],
    [InlineKeyboardButton(text='👀 В поиске себя',
                          callback_data='search_myself')]
])


# Главное меню
users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔎 Найти пользователей',
                          callback_data='users')],
    [InlineKeyboardButton(text='👋 Мои реакции',
                          callback_data='all_reactions')],
    [InlineKeyboardButton(text='✏️ Редактировать профиль',
                          callback_data='my_profile')],
    [InlineKeyboardButton(text='📬 Оставить отзыв',
                          callback_data='feedback')]
])


# меню реакций
reactions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📤 Исходящие запросы',
                          callback_data='my_reactions')],
    [InlineKeyboardButton(text='📥 Входящие запросы',
                          callback_data='incoming_reactions_list')],
    # [InlineKeyboardButton(text='📌 Избранное',
    # callback_data='favorite_users')],
    [InlineKeyboardButton(text='🤝 Мои контакты',
                          callback_data='match_reactions_list')],
    [InlineKeyboardButton(text='🚷 Скрытые пользователи',
                          callback_data='ignore_list')],
    [InlineKeyboardButton(text='↩️ Вернуться назад',
                          callback_data='main_menu')]
])


# уведомление о входящей реакции
def incoming_request_reaction(current_user_id):

    request_reaction = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Ответить 👋',
                              callback_data=f'accept_request:{current_user_id}'),
         InlineKeyboardButton(text='Отложить 💤',
                              callback_data=f'accept_late:{current_user_id}')]
    ])
    return request_reaction


# кнопка для "всплывающего" уведомления с удалением сообщения уведомления
error_add_to_contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Понятно 👌',
                          callback_data='close_notification')]
])


# кнопка для "всплывающего" уведомления с возвратом в меню реакций
error_add_to_contacts_from_reactions_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Понятно 👌',
                          callback_data='all_reactions')]
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
        [InlineKeyboardButton(text='Закрыть уведомление',
                              callback_data='close_notification')]
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
     InlineKeyboardButton(text='🌇 Город',
                          callback_data='edit_city')],
    [InlineKeyboardButton(text='📇 "О себе"',
                          callback_data='edit_about_me'),
     InlineKeyboardButton(text='💼 Занятость',
                          callback_data='edit_employment')],
    [InlineKeyboardButton(text='🗑 Удалить профиль',
                          callback_data='delete_profile')],
    [InlineKeyboardButton(text='↩️ Главное меню', callback_data='main_menu')]])


# Редактирование хобби
edit_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить увлечение',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='➖ Удалить увлечение',
                          callback_data='del_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# если у пользователя нет увлечений - выводится без кнопки "удалить увлечение"
no_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить увлечение',
                          callback_data='new_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# если у пользователя максимальное количество увлечений (клавиатура без кнопки добавить)
max_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➖ Удалить увлечение',
                          callback_data='del_hobby')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# вернутьсяв меню редактирования увлечений
back_hobbies = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_hobbies')]])


# Функция формирования клавиатуры с кнопкой для удаления каждого увлечение
def delete_hobbies_keyboard(user_tg_id, hobbies):
    builder = InlineKeyboardBuilder()

    for hobby in hobbies:

        # сохраняю полное имя хобби для получения его id
        full_name_hobby = hobby

        # сокращаю имя хобби для эстетичного вывода в тексте кнопки
        if len(hobby) > 30:
            hobby = hobby[:40]+'...'

        # получаю id хобби
        hobby_id = get_hobby_id_by_hobby_name(user_tg_id, full_name_hobby)

        # отрисовка кнопок со всеми хобби в списке
        button = InlineKeyboardButton(
            text=f'🚫 {hobby}', callback_data=f'remove_hobby:{hobby_id}')
        builder.row(button)  # Добавляем каждую кнопку в отдельной строке

    # Добавляем кнопку "Назад" в отдельной строке
    back_button = InlineKeyboardButton(
        text="↩️ Вернуться назад", callback_data="edit_hobbies")
    builder.row(back_button)

    return builder.as_markup()


# Редактирование фото профиля
edit_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='🗑 Удалить фото', callback_data='del_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# выводится если у пользователя нет фото (без кнопки удалить фото профиля)
edit_no_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📸 Загрузить новое фото',
                          callback_data='new_photo')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# выход из редактирования фото профиля
back_to_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='edit_photo')]])


# Общий возврат в мой профиль
back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# Общий возврат в главное меню
back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ В главное меню', callback_data='main_menu')]])

# Меню редактирования раздела "О себе"
edit_about_me = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Редактировать "О себе"',
                          callback_data='add_about_me')],
    [InlineKeyboardButton(text='➖ Удалить "О себе"',
                          callback_data='delete_about_me')],
    [InlineKeyboardButton(text='↩️ Вернуться назад',
                          callback_data='my_profile')]
])


# Меню редактирования раздела "О себе" без кнопки удалить (если раздел пуст)
edit_about_me_no_delete_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить "О себе"',
                          callback_data='add_about_me')],
    [InlineKeyboardButton(text='↩️ Вернуться назад',
                          callback_data='my_profile')]
])


# редактирование работы/учебы
edit_job_or_study = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💼 Работаю', callback_data='work')],
    [InlineKeyboardButton(text='📚 Учусь', callback_data='study')],
    [InlineKeyboardButton(text='👀 В поиске себя',
                          callback_data='search_myself')],
    [InlineKeyboardButton(text='↩️ Вернуться назад',
                          callback_data='my_profile')]
])


# Редактирование пола
edit_gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female')],
    [InlineKeyboardButton(text='Не указывать', callback_data='other')],
    [InlineKeyboardButton(text='↩️ Вернуться назад', callback_data='my_profile')]])


# выводится после регистрации нового пользователя
start_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✏️ Заполнить профиль',
                          callback_data='my_profile')],
    [InlineKeyboardButton(text='↩️ В главное меню', callback_data='main_menu')]])


# Поиск пользователей
users_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗃 Все пользователи',
                          callback_data='all_users')],
    [InlineKeyboardButton(text='🎛 Расширенный поиск',
                          callback_data='advanced_search')],
    [InlineKeyboardButton(text='↩️ Главное меню', callback_data='main_menu')]])


# Выбор пола для поиска
gender_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍🦰', callback_data='male-search')],
    [InlineKeyboardButton(text='👩‍🦰', callback_data='female-search')],
    [InlineKeyboardButton(text='Не важно', callback_data='all-search')],
    [InlineKeyboardButton(text='↩️ Выйти в меню', callback_data='users')]])


# выбор города для поиска
def search_in_city(home_city):
    city_search = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'🌇 В моем городе ({home_city})',
                              callback_data='home_city')],
        [InlineKeyboardButton(text='Не важно', callback_data='all_cities')],
        [InlineKeyboardButton(text='↩️ Выйти в меню', callback_data='users')]])
    return city_search


# выбор хобби для поиска
hobbies_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎸 По моим увлечениям',
                          callback_data='my_hobbies')],
    [InlineKeyboardButton(text='Не важно', callback_data='all_hobbies')],
    [InlineKeyboardButton(text='↩️ Выйти в меню', callback_data='users')]
])

# изменить один из параметров поиска (?)
'''
change_search_params = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⚧️ Пол',
                          callback_data='change_gender_search')],
    [InlineKeyboardButton(text='🌇 Город', callback_data='change_city_search')],
    [InlineKeyboardButton(text='🎸 Увлечения',
                          callback_data='change_hobby_search')],
    [InlineKeyboardButton(text='↩️ Выйти в меню',
                          callback_data='change_hobby_search')]
])
'''


# назад к поиску
search_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️ В меню поиска', callback_data='users')]
])


# Удаление профиля
delete_profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='confirm_delete'),
     InlineKeyboardButton(text='Нет', callback_data='my_profile')],

])


# класс пагинации поиска пользователей
class Pagination(CallbackData, prefix='pg'):
    action: str
    page: int
    list_type: str


# клавиатура пагинации
def paginator(page: int = 0, list_type: str = 'default', action: str = 'like', total_pages: int = 1):
    builder = InlineKeyboardBuilder()

    # Логика для текста кнопок "Назад" и "Вперед"
    # Стрелка только если не на первой странице
    prev_text = '◀️' if page > 0 else ' '
    # Стрелка только если не на последней странице
    next_text = '▶️' if page < total_pages - 1 else ' '

    # Логика для callback_data: создаём её только если кнопка активна
    prev_callback = Pagination(
        action='prev', page=page, list_type=list_type).pack() if page > 0 else None
    next_callback = Pagination(action='next', page=page,
                               list_type=list_type).pack() if page < total_pages - 1 else None

    # Первый ряд: кнопки "Назад", "Меню", "Вперед"
    builder.row(
        InlineKeyboardButton(
            text=prev_text, callback_data=prev_callback or 'ignore'),
        InlineKeyboardButton(text='↩️ Меню', callback_data=Pagination(
            action='menu', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(
            text=next_text, callback_data=next_callback or 'ignore')
    )

    # Второй ряд: кнопка "Отправить реакцию" и добавить в избранное
    builder.row(
        # InlineKeyboardButton(text='В избранное 📌', callback_data=Pagination(
        # action='to_favorite', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(text='Отправить 👋', callback_data=Pagination(
            action='like', page=page, list_type=list_type).pack())
    )

    # Третий ряд: кнопка "Скрыть"
    builder.row(
        InlineKeyboardButton(text='Скрыть пользователя 🚷', callback_data=Pagination(
            action='hide', page=page, list_type=list_type).pack())
    )

    return builder.as_markup()


# Клавиатуры пагинации просмотра реакций
class PaginationLikes(CallbackData, prefix='pg_likes'):
    action: str
    page: int
    list_type: str


# клавиатура просмотра "моих реакций"
def paginator_likes(page: int = 0, list_type: str = 'default', action: str = 'in_reactions_dislike', total_pages: int = 1):
    builder = InlineKeyboardBuilder()

    # Логика для текста кнопок "Назад" и "Вперед"
    # Стрелка только если не на первой странице
    prev_text = '◀️' if page > 0 else ' '
    # Стрелка только если не на последней странице
    next_text = '▶️' if page < total_pages - 1 else ' '

    # Логика для callback_data: создаём её только если кнопка активна
    prev_callback = PaginationLikes(
        action='prev_likes', page=page, list_type=list_type).pack() if page > 0 else None
    next_callback = PaginationLikes(action='next_likes', page=page,
                                    list_type=list_type).pack() if page < total_pages - 1 else None

    # Первый ряд: кнопки "Назад", "Вперед" и "Меню"
    builder.row(
        InlineKeyboardButton(
            text=prev_text, callback_data=prev_callback or 'ignore'),
        InlineKeyboardButton(text='↩️ Меню', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(
            text=next_text, callback_data=next_callback or 'ignore')
    )

    # Второй ряд: кнопка "Отменить реакцию"
    builder.row(
        InlineKeyboardButton(text='Отменить реакцию 🚫', callback_data=PaginationLikes(
            action='in_reactions_dislike', page=page, list_type=list_type).pack())
    )

    return builder.as_markup()


# клавиатура просмотра "входящих реакций"
def incoming_reactions(page: int = 0, list_type: str = 'default', action: str = 'in_reactions_like', total_pages: int = 1):
    builder = InlineKeyboardBuilder()

    # Логика для текста кнопок "Назад" и "Вперед"
    # Стрелка только если не на первой странице
    prev_text = '◀️' if page > 0 else ' '
    # Стрелка только если не на последней странице
    next_text = '▶️' if page < total_pages - 1 else ' '

    # Логика для callback_data: создаём её только если кнопка активна
    prev_callback = PaginationLikes(
        action='prev_likes', page=page, list_type=list_type).pack() if page > 0 else None
    next_callback = PaginationLikes(action='next_likes', page=page,
                                    list_type=list_type).pack() if page < total_pages - 1 else None

    # Первый ряд: кнопки "Назад", "Вперед" и "Меню"
    builder.row(
        InlineKeyboardButton(
            text=prev_text, callback_data=prev_callback or 'ignore'),
        InlineKeyboardButton(text='↩️ Меню', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(
            text=next_text, callback_data=next_callback or 'ignore')
    )

    # Второй ряд: кнопки "Ответить"
    builder.row(
        InlineKeyboardButton(text='Ответить 👋', callback_data=PaginationLikes(
            action='in_reactions_like', page=page, list_type=list_type).pack())
    )

    # Третий ряд: кнопка "Не интересно"
    builder.row(
        InlineKeyboardButton(text='Не интересно 🚫', callback_data=PaginationLikes(
            action='delete_incoming', page=page, list_type=list_type).pack())
    )

    return builder.as_markup()


# клавиатура просмотра "моих контактов"
def match_reactions_pagination(page: int = 0, list_type: str = '', nickname: str = '', action: str = 'start_chat', total_pages: int = 1):
    builder = InlineKeyboardBuilder()

    # Логика для текста кнопок "Назад" и "Вперед"
    # Стрелка только если не на первой странице
    prev_text = '◀️' if page > 0 else ' '
    # Стрелка только если не на последней странице
    next_text = '▶️' if page < total_pages - 1 else ' '

    # Логика для callback_data: создаём её только если кнопка активна
    prev_callback = PaginationLikes(
        action='prev_likes', page=page, list_type=list_type).pack() if page > 0 else None
    next_callback = PaginationLikes(action='next_likes', page=page,
                                    list_type=list_type).pack() if page < total_pages - 1 else None

    # Первый ряд: кнопки "Назад", "Вперед" и "Меню"
    builder.row(
        InlineKeyboardButton(
            text=prev_text, callback_data=prev_callback or 'ignore'),
        InlineKeyboardButton(text='↩️ Меню', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(
            text=next_text, callback_data=next_callback or 'ignore')
    )

    # Второй ряд: кнопка "Чат"
    builder.row(
        InlineKeyboardButton(text='✉️ Чат', url=f'https://t.me/{nickname}'),
    )

    # Третий ряд: кнопка "Удалить"
    builder.row(
        InlineKeyboardButton(text='🚫 Удалить', callback_data=PaginationLikes(
            action='delete_contact', page=page, list_type=list_type).pack())
    )

    return builder.as_markup()


# клавиатура просмотра "скрытых пользователей"
def ignored_users_pagination(page: int = 0, list_type: str = 'ignore_users_list', action: str = 'start_dialog', total_pages: int = 1):
    builder = InlineKeyboardBuilder()

    # Логика для текста кнопок "Назад" и "Вперед"
    # Стрелка только если не на первой странице
    prev_text = '◀️' if page > 0 else ' '
    # Стрелка только если не на последней странице
    next_text = '▶️' if page < total_pages - 1 else ' '

    # Логика для callback_data: создаём её только если кнопка активна
    prev_callback = PaginationLikes(
        action='prev_likes', page=page, list_type=list_type).pack() if page > 0 else None
    next_callback = PaginationLikes(action='next_likes', page=page,
                                    list_type=list_type).pack() if page < total_pages - 1 else None

    # Первый ряд: кнопки "Назад", "Вперед" и "Меню"
    builder.row(
        InlineKeyboardButton(
            text=prev_text, callback_data=prev_callback or 'ignore'),
        InlineKeyboardButton(text='↩️ Меню', callback_data=PaginationLikes(
            action='menu_likes', page=page, list_type=list_type).pack()),
        InlineKeyboardButton(
            text=next_text, callback_data=next_callback or 'ignore')
    )

    # Второй ряд: кнопка "Вернуть в поиск"
    builder.row(
        InlineKeyboardButton(text='♻️ Вернуть в поиск', callback_data=PaginationLikes(
            action='remove_from_ignore', page=page, list_type=list_type).pack())
    )

    return builder.as_markup()
