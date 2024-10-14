import asyncio
import logging
import random
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from config import delete_profile_id, in_progress
from aiogram.exceptions import TelegramBadRequest
from src.modules.pagination_logic import no_data_after_reboot_bot, back_callback, load_pagination, load_pagination_bot
from src.modules.notifications import (loader,
                                       bot_notification_about_like,
                                       bot_send_message_about_like,
                                       bot_send_message_matchs_likes)

from src.modules.delete_messages import del_last_message
from src.database.requests.user_data import get_data, get_user_data
from src.modules.get_self_data import get_user_info
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.handlers.edit_name import check_emodji
from src.database.requests.search_users import (get_users_by_hobby,
                                                check_users_by_city,
                                                check_users_self_city,
                                                check_users_by_self_hobby,
                                                get_stemmed_self_hobbies)

from src.handlers.edit_hobbies import wrong_search_hobby_name
from src.handlers.edit_city import wrong_search_city_name
from src.database.requests.likes_users import (insert_reaction,
                                               delete_and_insert_reactions,
                                               get_liked_users_ids,
                                               check_matches_two_users,
                                               get_ignore_users_ids)
import src.modules.keyboard as kb

router = Router()

# изменение пути nltk_data для подключения списка "стоп" слов
nltk.data.path.append('/Users/dude/dev/python/tele_bot/nltk_data')

# Инициализация стеммера и списка стоп-слов
language = 'russian'

# Инициализация стеммера для русского языка
stemmer = SnowballStemmer(language)

# инициализация списка "стоп" слов
stop_words = set(stopwords.words(language))


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Меню "пользователи"


@router.callback_query(F.data == 'users')
async def check_users_menu(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users_menu
        )
    except:
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.users_menu
        )


# оработчик колбэков меню поиска


@router.callback_query(F.data.in_(['advanced_search', 'all_users']))
async def search_users_menu(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = callback.data

    # добавляю в состояниие инфу о выбраном меню чтобы обработать вывод клавиатуры далее
    await state.update_data(type_of_search=data)

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    # отрисовка сообщения с клавиатурой
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}\n\n'
                    '<b>Кого ищем?</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                '<b>Кого ищем?</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.gender_search
        )


# Выбор пола для поиска пользователей


@router.callback_query(F.data.in_(['male-search', 'female-search', 'all-search']))
async def choise_gender_for_search(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    search_data = data.get('type_of_search')
    gender_data = callback.data

    # изменение callback.data из-за конфликта с другой клавиатурой
    if gender_data == 'male-search':
        gender_data = 'male'
    elif gender_data == 'female-search':
        gender_data = 'female'
    elif gender_data == 'all-search':
        gender_data = 'all'

    if search_data == 'all_users':
        await search_all_users(callback, state, gender_data)
    elif search_data == 'advanced_search':
        await state.update_data(type_of_gender=gender_data)
        await serach_users_by_city(callback, state)


# Поиск пользователей в городе (УДАЛИТЬ)

'''
async def search_users_in_city(callback, state, gender_data):

    user_tg_id = callback.from_user.id

    ignore_users_ids = await asyncio.to_thread(get_ignore_users_ids, user_tg_id)
    liked_users_ids = await asyncio.to_thread(get_liked_users_ids, user_tg_id)

    # объединяю оба множества
    ignore_list = ignore_users_ids | liked_users_ids

    # получаю готовый список пользователей
    data = await asyncio.to_thread(get_users_in_city, user_tg_id, gender_data, ignore_list)

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    if not data:

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}\n\n'
                    '❌ <b>Пользователи в вашем городе не найдены</b>\n'
                    '🔎 Попробуйте изменить параметры поиска.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )

    else:

        gender = await check_gender(data[0][4])
        hobbies = await hobbies_list(data[0][7])
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][2]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][1]}\n'
                    f'<b>Возраст:</b> {data[0][5]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][6]}\n'
                    f'<b>Увлечения:</b> {hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.paginator(
                list_type='hobbies_users')
        )

        await state.update_data(users_data=data)
'''

# ================================
# ПОИСК ЛЮДЕЙ ПО ГОРОДАМ         |
# ================================


async def serach_users_by_city(callback, state):

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n<b>В каком городе будем искать?</b>'
                '\n\n<b>Выберите один из вариантов ниже...</b> ⌨️'
                '\n\n<i>...или пришлите в чат <b>название города</b>, '
                'в котором хотите найти пользователей:</i>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.city_search
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.search_city)


# поиск в моем городе или в любом


@router.callback_query(F.data.in_(['home_city', 'all_cities']))
async def search_in_city(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    search_data = callback.data

    # получаю данные пола из состояния
    gender_data = await state.get_data()
    search_gender = gender_data.get('type_of_gender')

    if search_data == 'home_city':

        # проверяю наличие пользователей по запрошенному полу в своем городе
        home_city_users = await asyncio.to_thread(check_users_self_city,
                                                  user_tg_id,
                                                  search_gender)

        if home_city_users:

            await search_users_by_hobby(callback, state)

        else:
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{in_progress}',
                        caption=(
                            '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                            '\n\nВы можете выбрать пункт <b>"Не важно"</b> '
                            'чтобы посмотреть пользователей во всех городах...'
                            '\n\n<i>...или пришлите в чат название города, '
                            'чтобы найти в нем пользователей:</i>'
                        ),
                        parse_mode='HTML'
                    ),
                    reply_markup=kb.city_search
                )
            except:
                await callback.message.answer_photo(
                    photo=f'{in_progress}',
                    caption=(
                        '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                        '\n\nВы можете выбрать пункт <b>"Не важно"</b> '
                        'чтобы посмотреть пользователей во всех городах...'
                        '\n\n<i>...или пришлите в чат название города, '
                        'чтобы найти в нем пользователей:</i>'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.city_search
                )
            await state.set_state(Registration.search_city)

    elif search_data == 'all_cities':
        await state.update_data(city_users='all')
        await search_users_by_hobby(callback, state)


# поиск по конкретному городу


@router.message(Registration.search_city)
async def search_by_city(message: Message, state: FSMContext, bot: Bot):

    user_tg_id = message.from_user.id

    # удаляю сообщение отправленное в чат
    await del_last_message(message)

    # получаю данные запроса пола
    gender_data = await state.get_data()
    search_gender = gender_data.get('type_of_gender')

    # получаю id сообщения для редактирования
    edit_message = await state.get_data()
    message_id = edit_message.get('message_id')

    # проверка что сообщение текстовое, а не медиа (картинки, стикеры и т.д.)
    if message.content_type == 'text':
        city_name = message.text.title()

        # проверка на наличие смайлов в сообщении
        emodji_checked = await check_emodji(city_name)

        if not emodji_checked:
            await wrong_search_city_name(user_tg_id, message_id, bot)
            return

        # проверяю наличие хотя бы одного пользователя по уловиям
        search_city_users = await asyncio.to_thread(check_users_by_city,
                                                    user_tg_id,
                                                    city_name,
                                                    search_gender)

        if not search_city_users:

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        f'\n❌ Пользователи в городе <b>{city_name}</b> '
                        'не найдены.'
                        '\n\nВы можете выбрать пункт <b>"Не важно"</b> '
                        'чтобы посмотреть пользователей во всех городах...'
                        '\n\n<b>...или пришлите в чат название другого города, '
                        'в котором хотите найти пользователей:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.city_search
            )

        else:

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        '<b>Выберите один из вариантов ниже...</b> ⌨️'
                        '\n\n... или пришлите <b>название увлечения</b> в чат, '
                        'по которому хотите найти пользователей:'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.hobbies_search
            )
            await state.update_data(city_users=city_name)
            await state.set_state(Registration.search_hobby)


# ================================
# ПОИСК ЛЮДЕЙ ПО ХОББИ           |
# ================================


async def search_users_by_hobby(callback, state):

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '<b>\nВыберите один из вариантов ниже...</b> ⌨️'
                '\n\n... или пришлите <b>название увлечения</b> в чат, '
                'по которому хотите найти пользователей:'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.hobbies_search
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.search_hobby)


# по моим хобби или по любым


@router.callback_query(F.data.in_(['my_hobbies', 'all_hobbies']))
async def my_hobbies_or_all(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    search_data = callback.data

    # получаю данные пола из состояния
    gender_data = await state.get_data()
    search_gender = gender_data.get('type_of_gender')

    # списки user_tg_ids для исключения из поиска:
    # получаю id пльзователей, которых не надо выводить в поиске
    ignore_users_ids = await asyncio.to_thread(get_ignore_users_ids, user_tg_id)
    liked_users_ids = await asyncio.to_thread(get_liked_users_ids, user_tg_id)

    # объединяю оба множества
    ignore_list = ignore_users_ids | liked_users_ids

    if search_data == 'my_hobbies':

        # поверяю есть ли хотя бы одно хобби у "меня"
        check_my_hobbies = await asyncio.to_thread(check_users_by_self_hobby,
                                                   user_tg_id)

        if check_my_hobbies:
            # список моих хобби пропущенных через стемминг и готовых для поиска
            my_hobbies_list = await asyncio.to_thread(get_stemmed_self_hobbies,
                                                      user_tg_id)

            # TODO ПЕРЕДАТЬ СПИСКИ ID ДЛЯ ИСКЛЮЧЕНИЯ
            await asyncio.to_thread(get_users_by_hobby,
                                    my_hobbies_list,
                                    user_tg_id,
                                    search_gender,
                                    ignore_list)
        else:
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{in_progress}',
                        caption=(
                            '\n❌ <b>Пользователи в данном городе и с схожими '
                            'увлечениям не найдены.</b>'
                            '\n\nПопробуйте изменить параметры поиска, например '
                            'выберите другой <b>город</b> или <b>пол</b>.'
                            '\nВы также можете выбрать один из предложенных '
                            'вариантов поиска по увлечениям...'
                            '\n\n...или просто пришлите мне новое увлечение в чат:'
                        ),
                        parse_mode='HTML'
                    ),
                    reply_markup=kb.hobbies_search
                )
            except:
                await callback.message.answer_photo(
                    photo=f'{in_progress}',
                    caption=(
                        '\n❌ <b>Пользователи в данном городе и с схожими '
                        'увлечениям не найдены.</b>'
                        '\n\nПопробуйте изменить параметры поиска, например '
                        'выберите другой <b>город</b> или <b>пол</b>.'
                        '\nВы также можете выбрать один из предложенных '
                        'вариантов поиска по увлечениям...'
                        '\n\n...или просто пришлите мне новое увлечение в чат:'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.hobbies_search
                )
            await state.set_state(Registration.search_hobby)

    elif search_data == 'all_hobbies':

        hobbies = 'all'
        # TODO ПЕРЕДАТЬ СПИСКИ ID ДЛЯ ИСКЛЮЧЕНИЯ
        await asyncio.to_thread(hobbies,
                                my_hobbies_list,
                                user_tg_id,
                                search_gender,
                                ignore_list)


# по конкретному хобби


@router.message(Registration.search_hobby)
async def search_by_hobby(message: Message, state: FSMContext, bot: Bot):
    await del_last_message(message)

    user_tg_id = message.from_user.id
    gender_type = await state.get_data()
    gender_data = gender_type.get('type_of_gender')

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    edit_message = await state.get_data()
    message_id = edit_message.get('message_id')

    if message.content_type == 'text':
        request = message.text.lower()

        # проверка на наличие смайлов в сообщении
        emodji_checked = await check_emodji(request)

        if not emodji_checked:
            await wrong_search_hobby_name(user_tg_id, message_id, bot)
            return

        # разделяю строку на отдельные слова
        words_for_stemmed = request.split()

        # Фильтрую стоп-слова
        filtered_words = [
            word for word in words_for_stemmed if word not in stop_words
        ]

        # применяю стемминг к оставшимся словам
        stemmed_words = [stemmer.stem(word) for word in filtered_words]

        # получаю id пльзователей, которых не надо выводить в поиске
        ignore_users_ids = await asyncio.to_thread(get_ignore_users_ids, user_tg_id)
        liked_users_ids = await asyncio.to_thread(get_liked_users_ids, user_tg_id)

        # объединяю оба множества
        ignore_list = ignore_users_ids | liked_users_ids

        # получаю готовый список пользователей
        data = await asyncio.to_thread(get_users_by_hobby, stemmed_words, user_tg_id, gender_data, ignore_list)

        if not data:

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        '\n❌ <b>Пользователи с таким увлечением не найдены.</b>'
                        '\n\nПопробуйте изменить параметры поиска, например '
                        'выберите другой <b>город</b> или <b>пол</b>.'
                        '\nВы также можете выбрать один из предложенных '
                        'вариантов поиска по увлечениям...'
                        '\n\n...или просто пришлите мне новое увлечение в чат:'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.hobbies_search
            )

        else:
            await state.clear()

            await load_pagination_bot(bot,
                                      user_tg_id,
                                      message_id,
                                      data,
                                      'paginator',
                                      'hobbies_users')

            await state.update_data(users_data=data)

    else:
        await wrong_search_hobby_name(user_tg_id, message_id, bot)

# Отображение всех пользователей


async def search_all_users(callback, state, gender_data):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    try:
        # получаю списки пользователей для исключения
        ignore_users_ids = await asyncio.to_thread(get_ignore_users_ids, user_tg_id)
        liked_users_ids = await asyncio.to_thread(get_liked_users_ids, user_tg_id)

        # объединяю оба множества
        ignore_list = ignore_users_ids | liked_users_ids

        # получаю готовый список пользователей
        data = await asyncio.to_thread(get_data, user_tg_id, gender_data, ignore_list)
    except Exception as e:
        print(f'SHOW ALL USERS ERROR: {e}')

    if not data:

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{in_progress}',
                caption=(
                    '\n❌ <b>Пользователи не найдены</b>'
                    '\n\n🔎 Попробуйте изменить параметры поиска.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )

    else:
        await load_pagination(callback.message,
                              data,
                              'paginator',
                              'all_users')

        await state.update_data(users_data=data)


# Пагинация списка пользователей

@router.callback_query(
    kb.Pagination.filter(F.action.in_(
        ['prev',
         'next',
         'menu',
         'like']
    ))
)
async def pagination_handler(
    callback: CallbackQuery,
    callback_data: kb.Pagination,
    state: FSMContext,
    bot: Bot
):
    user_tg_id = callback.message.chat.id
    list_type = callback_data.list_type

    data = (await state.get_data()).get('users_data')

    # если бот ушел в ребут с открытой пагинацией у пользователя
    if not data:
        await no_data_after_reboot_bot(callback)

    # Загрузка пагинации если data не None
    else:
        page_num = int(callback_data.page)

        if callback_data.action == 'prev':
            page = max(page_num - 1, 0)
        elif callback_data.action == 'next':
            page = min(page_num + 1, len(data) - 1)
        else:
            page = page_num

        # нажатие на кнопку "Назад"
        if callback_data.action == 'menu':

            # Выход из пагинации (четвертый параметр - текст под инфой пользователя (не обязательный))
            await back_callback(callback.message, user_tg_id, 'users_menu')

        # лайк карточки пользователя
        elif callback_data.action == 'like':

            current_user_id = data[page][0]

            # добавление записи в бд
            await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)

            # уведомление пользователю
            await bot_send_message_about_like(user_tg_id, current_user_id, bot)

            # всплывающее уведомление
            await bot_notification_about_like(callback.message, f'{data[page][1]}')

            # удаляем лайкнутого пользователя из data
            data.pop(page)

            # если False (data пустая)
            if not data:

                # выводим сообщение об отсутствии пользователей
                text_info = '<b>Список пользователей пуст</b> 🤷‍♂️'
                await back_callback(callback.message,
                                    user_tg_id,
                                    'search_users',
                                    text_info)

            # если True (data не пустая)
            else:

                # Обновляем номер страницы
                if page >= len(data):

                    # Переход на последнюю страницу, если текущая выходит за пределы
                    page = len(data) - 1

                    # отрисовываю клавиатуру с учетом изменений
                await load_pagination(callback.message,
                                      data,
                                      'paginator',
                                      list_type,
                                      page)

            # поверка наличи ответных записей в userreactions
            check = await asyncio.to_thread(check_matches_two_users, user_tg_id, current_user_id)

            # если запись есть
            if check:

                # удаляем записи из userreactions и переносим в matchreactions
                await asyncio.to_thread(delete_and_insert_reactions, user_tg_id, current_user_id)

                # функция отправки сообщения обоим пользователям
                await bot_send_message_matchs_likes(user_tg_id, current_user_id, bot, callback)

                # загружаю клавиатуру с учетом изменений
                await load_pagination(callback.message,
                                      data,
                                      'paginator',
                                      list_type,
                                      page)

        else:

            # убирает ошибку если пользователи в пагинации закончились
            with suppress(TelegramBadRequest):

                # отрисовывает клавиатуру даже если пользователи кончились
                await load_pagination(callback.message,
                                      data,
                                      'paginator',
                                      list_type,
                                      page)

    await callback.answer()
