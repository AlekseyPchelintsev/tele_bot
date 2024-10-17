'''
import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from config import delete_profile_id, in_progress
from aiogram.exceptions import TelegramBadRequest
from src.modules.pagination_logic import no_data_after_reboot_bot, back_callback, load_pagination, load_pagination_bot
from src.modules.notifications import (loader,
                                       attention_message,
                                       bot_notification_about_like,
                                       bot_send_message_about_like,
                                       bot_send_message_matchs_likes)

from src.modules.delete_messages import del_last_message
from src.database.requests.user_data import get_all_users_data
from src.modules.get_self_data import get_user_info
from src.handlers.edit_name import check_emodji
from src.database.requests.search_users import (check_users_in_city,
                                                get_stemmed_hobbies_list,
                                                check_users_by_hobbies,
                                                search_users)

from src.handlers.edit_hobbies import wrong_search_hobby_name
from src.handlers.edit_city import wrong_search_city_name
from src.database.requests.likes_users import (insert_reaction,
                                               delete_and_insert_reactions,
                                               check_matches_two_users)
import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# Меню "пользователи"


@router.callback_query(F.data == 'users')
async def check_users_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (контрольно)
    await state.clear()

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные
    self_data = user_info['data']

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '🔎 <b>Выберите один из вариантов поиска:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users_menu
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                '🔎 <b>Выберите один из вариантов поиска:</b>'
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

    # Извлекаю свои данные
    self_data = user_info['data']

    # отрисовка сообщения с клавиатурой
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '\n\n<b>🔎 Кого ищем?</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                '\n\n<b>🔎 Кого ищем?</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.gender_search
        )


# Выбор пола для поиска пользователей


@router.callback_query(F.data.in_(['male-search', 'female-search', 'all-search']))
async def choise_gender_for_search(callback: CallbackQuery, state: FSMContext):

    print(f'ВЫБРАН ПОЛ: {callback.data}')

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


# ================================
# ПОИСК ЛЮДЕЙ ПО ГОРОДАМ         |
# ================================


async def serach_users_by_city(callback, state):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)
    city_data = user_info['data'][0][5]

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>В каком городе?</b>'
                '\n\n📌💬 Пришлите <b>название города</b> в чат'
                '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_in_city(city_data)
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.search_city)


# поиск в моем городе или в любом


@router.callback_query(F.data.in_(['home_city', 'all_cities']))
async def search_in_city(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    search_data = callback.data

    # получаю данные пола из состояния
    search_gender = await state.get_data()
    gender_data = search_gender.get('type_of_gender')

    if search_data == 'home_city':

        # плучаю свои данные
        user_info = await get_user_info(user_tg_id)

        # Извлекаю название своего города
        city_data = user_info['data'][0][5]

        print(f'ВЫБРАН ПОИСК В МОЕМ ГОРОДЕ')
        print(f'ДАННЫЕ ГОРОДА: {city_data}, ПОЛА:{gender_data}')

        # проверяю наличие пользователей по запрошенному полу в своем городе
        check_home_city_users = await asyncio.to_thread(check_users_in_city,
                                                        user_tg_id,
                                                        city_data,
                                                        gender_data)

        if check_home_city_users:

            print(f'ПОЛЬЗОВАТЕЛИ В МОЕМ ГОРОДЕ ПО ПОЛУ НАЙДЕНЫ')

            # добавляю в состояние название своего города
            await state.update_data(city_users=city_data)
            await search_users_by_hobby(callback, state)

        else:

            print(f'ПОЛЬЗОВАТЕЛИ В МОЕМ ГОРОДЕ ПО ПОЛУ НЕ НАЙДЕНЫ')

            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{in_progress}',
                        caption=(
                            '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                            '\n\n📌⌨️ Вы можете выбрать пункт <b>"Не важно"</b> '
                            'чтобы посмотреть пользователей во всех городах'
                            '\n\n📌💬 или <b>пришлите в чат</b> название города, '
                            'чтобы найти в нем пользователей:'
                        ),
                        parse_mode='HTML'
                    ),
                    reply_markup=kb.search_in_city(city_data)
                )
            except:
                await callback.message.answer_photo(
                    photo=f'{in_progress}',
                    caption=(
                        '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                        '\n\n📌⌨️ Вы можете выбрать пункт <b>"Не важно"</b> '
                        'чтобы посмотреть пользователей во всех городах'
                        '\n\n📌💬 или <b>пришлите в чат</b> название города, '
                        'чтобы найти в нем пользователей:'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.search_in_city(city_data)
                )
            await state.set_state(Registration.search_city)

    elif search_data == 'all_cities':

        print('ВЫБРАН ПОИСК ПО ВСЕМ ГОРОДАМ')

        await state.update_data(city_users='all')
        await search_users_by_hobby(callback, state)


# поиск по конкретному городу


@router.message(Registration.search_city)
async def search_by_city(message: Message, state: FSMContext, bot: Bot):

    print(f'НАЗВАНИЕ ГОРОДА ОТПРАВЛЕНО В ЧАТ')

    user_tg_id = message.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)
    # Извлекаю название своего города
    city_data = user_info['data'][0][5]

    # удаляю сообщение отправленное в чат
    await del_last_message(message)

    # получаю данные пола из состояния
    search_gender = await state.get_data()
    gender_data = search_gender.get('type_of_gender')

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
        check_users_city = await asyncio.to_thread(check_users_in_city,
                                                   user_tg_id,
                                                   city_name,
                                                   gender_data)

        if check_users_city:

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        '\n🔎 <b>Какие увлечения?</b>'
                        '\n\n📌💬 Пришлите <b>увлечение</b> в чат'
                        '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.hobbies_search
            )

            await state.update_data(city_users=city_name)
            await state.set_state(Registration.search_hobby)

        else:

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        '\n🔎 <b>В каком городе?</b>'
                        f'\n\n❌ Пользователи в городе <b>"{city_name}"</b> '
                        '<u>не найдены.</u>'
                        '\n\n📌💬 Попробуйте поискать в <b>других городах</b>'
                        '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.search_in_city(city_data)
            )
    else:
        await wrong_search_city_name(user_tg_id, message_id, bot)
        return


# ================================
# ПОИСК ЛЮДЕЙ ПО ХОББИ           |
# ================================


async def search_users_by_hobby(callback, state):

    print(f'ЗАГРУЖЕНО МЕНЮ ПОИСК ПО ХОББИ')

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{in_progress}',
            caption=(
                '\n🔎 <b>Какие увлечения?</b>'
                '\n\n📌💬 Пришлите <b>увлечение</b> в чат'
                '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
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
    data_state = await state.get_data()
    gender_data = data_state.get('type_of_gender')
    city_data = data_state.get('city_users')

    if search_data == 'my_hobbies':

        print(f'ВЫБРАН ПОИСК ПО МОИМ ХОББИ')
        print(f'ДАННЫЕ В СОСТОЯНИИ - ПОЛ: {gender_data}, ГОРОД: {city_data}')

        # плучаю список своих хооби (прогоняю через стемминг) и удаляю стоп-слова
        my_hobbies_data = await asyncio.to_thread(get_stemmed_hobbies_list, user_tg_id=user_tg_id)

        if not my_hobbies_data:

            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{in_progress}',
                        caption=(
                            '\n🔎 <b>Какие увлечения?</b>'
                            '\n\n❌ <b>Список ваших увлечений пуст</b>'
                            '\n\nДобавтье увлечения в настройках профиля или '
                            'попробуйте изменить параметры поиска, например, '
                            'выбрав вариант <b>"Не важно"</b>...'
                            '\n\n📌💬 Вы также можете прислать <b>название увлечения</b> в чат'
                        ),
                        parse_mode='HTML'
                    ),
                    reply_markup=kb.hobbies_search
                )
            except:
                await callback.message.answer_photo(
                    photo=f'{in_progress}',
                    caption=(
                        '\n🔎 <b>Какие увлечения?</b>'
                        '\n\n❌ <b>Список ваших увлечений пуст</b>'
                        '\n\nДобавтье увлечения в настройках профиля или '
                        'попробуйте изменить параметры поиска, например, '
                        'выбрав вариант <b>"Не важно"</b>...'
                        '\n\n📌💬 Вы также можете прислать <b>название увлечения</b> в чат'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.hobbies_search
                )
            await state.set_state(Registration.search_hobby)

        else:

            print(f'МОИ ХОББИ: {my_hobbies_data}')

            # поверяю есть ли хотя бы одно хобби у "меня"
            check_users_by_my_hobbies = await asyncio.to_thread(check_users_by_hobbies,
                                                                user_tg_id,
                                                                gender_data,
                                                                city_data,
                                                                my_hobbies_data)

            print(f'РЕЗУЛЬТАТ ПРОВЕРКИ ПОИСКА ПО МОИМ ХОББИ '
                  f'{check_users_by_my_hobbies}')

            if check_users_by_my_hobbies:

                data = await asyncio.to_thread(search_users,
                                               user_tg_id,
                                               gender_data,
                                               city_data,
                                               my_hobbies_data)

                await state.clear()

                await loader(callback.message, 'Секунду, загружаю 🤔')

                await load_pagination(callback.message,
                                      data,
                                      'paginator',
                                      'hobbies_users')

                await state.update_data(users_data=data)

            else:
                try:
                    await callback.message.edit_media(
                        media=InputMediaPhoto(
                            media=f'{in_progress}',
                            caption=(
                                '\n🔎 <b>Какие увлечения?</b>'
                                '\n\n❌ <b>Пользователи в данном городе и с схожими '
                                'увлечениям не найдены 😔</b>'
                                '\n\nПопробуйте изменить параметры поиска, например, '
                                'выберите другой <b>город</b> или <b>пол</b>.'
                                '\n\n📌⌨️ Вы также можете <b>выбрать один из вариантов</b> ниже'
                                '\n\n📌💬 или прислать <b>название увлечения</b> в чат'

                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.hobbies_search
                    )
                except:
                    await callback.message.answer_photo(
                        photo=f'{in_progress}',
                        caption=(
                            '\n🔎 <b>Какие увлечения?</b>'
                            '\n\n❌ <b>Пользователи в данном городе и с схожими '
                            'увлечениям не найдены 😔</b>'
                            '\n\nПопробуйте изменить параметры поиска, например, '
                            'выберите другой <b>город</b> или <b>пол</b>.'
                            '\n\n📌⌨️ Вы также можете <b>выбрать один из вариантов</b> ниже'
                            '\n\n📌💬 или прислать <b>название увлечения</b> в чат'
                        ),
                        parse_mode='HTML',
                        reply_markup=kb.hobbies_search
                    )
                await state.set_state(Registration.search_hobby)

    elif search_data == 'all_hobbies':

        print(f'ВЫБРАН ПОИСК ПО ВСЕМ ХОББИ (НЕ ВАЖНО)')
        print(f'ДАННЫЕ В СОСТОЯНИИ - ПОЛ: {gender_data}, ГОРОД: {city_data}')

        try:
            hobbies_data = ['all']

            data = await asyncio.to_thread(search_users,
                                           user_tg_id,
                                           gender_data,
                                           city_data,
                                           hobbies_data)

            await state.clear()
            await loader(callback.message, 'Секунду, загружаю 🤔')
            await load_pagination(callback.message,
                                  data,
                                  'paginator',
                                  'hobbies_users')

            await state.update_data(users_data=data)

        except:

            await search_all_users(callback, state, gender_data)


# по конкретному хобби


@router.message(Registration.search_hobby)
async def search_by_hobby(message: Message, state: FSMContext, bot: Bot):
    await del_last_message(message)

    print(f'Я ОТПРАВИЛ ХОББИ В ЧАТ')

    user_tg_id = message.from_user.id
    data_state = await state.get_data()
    gender_data = data_state.get('type_of_gender')
    city_data = data_state.get('city_users')

    edit_message = await state.get_data()
    message_id = edit_message.get('message_id')

    if message.content_type == 'text':
        request = message.text.lower()

        # проверка на наличие смайлов в сообщении
        emodji_checked = await check_emodji(request)

        if not emodji_checked:
            await wrong_search_hobby_name(user_tg_id, message_id, bot)
            return

        # стемминг запроса и удаление стоп-слов
        stemmed_words = await asyncio.to_thread(get_stemmed_hobbies_list, hobby_name=request)

        print(f'ХОББИ ПРОШЛО ВСЕ ПРОВЕРКИ')
        print(f'ВЫБРАННЫЙ ГОРОД: {city_data}\nВЫБРАННЫЙ ПОЛ: '
              f'{gender_data}\nХОББИ ДЛЯ ПОИСКА: {stemmed_words}')

        # поверяю наличие хотя бы 1 пользователя по фильтру запроса
        check_users_by_my_hobbies = await asyncio.to_thread(check_users_by_hobbies,
                                                            user_tg_id,
                                                            gender_data,
                                                            city_data,
                                                            stemmed_words)

        if check_users_by_my_hobbies:

            # получаю готовый список пользователей
            data = await asyncio.to_thread(search_users,
                                           user_tg_id,
                                           gender_data,
                                           city_data,
                                           stemmed_words)

            print(f'ЗАГРУЗКА ПАГИНАЦИИ С ДАННЫМИ: {data}')

            await state.clear()

            await loader(message, 'Секунду, загружаю 🤔')

            await load_pagination_bot(bot,
                                      user_tg_id,
                                      message_id,
                                      data,
                                      'paginator',
                                      'hobbies_users')

            await state.update_data(users_data=data)

        else:

            print(f'СРАБОТАЛО УСЛОВИЕ ЕСЛИ НЕТ СОВПАДЕНИЙ ПО ХОББИ: '
                  f'{stemmed_words}')

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{in_progress}',
                    caption=(
                        '\n🔎 <b>Какие увлечения?</b>'
                        '\n\n❌ <b>Пользователи с такими увлечениями в данном '
                        'городе не найдены</b> 😔'
                        '\n\nПопробуйте изменить параметры поиска, например, '
                        'выберите другой <b>город</b> или <b>пол</b>.'
                        '\n\n📌⌨️ Вы также можете <b>выбрать один из вариантов</b> ниже'
                        '\n\n📌💬 или прислать <b>другое увлечение</b> в чат:'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.hobbies_search
            )

    else:
        await wrong_search_hobby_name(user_tg_id, message_id, bot)

# Отображение всех пользователей


async def search_all_users(callback, state, gender_data):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']

    try:

        # получаю готовый список пользователей
        data = await asyncio.to_thread(get_all_users_data, user_tg_id, gender_data)

    except Exception as e:
        print(f'SHOW ALL USERS ERROR: {e}')

    if data:
        await loader(callback.message, 'Секунду, загружаю 🤔')
        await load_pagination(callback.message,
                              data,
                              'paginator',
                              'all_users')

        await state.update_data(users_data=data)

    else:

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        '\n\n❌ <b>Пользователи не найдены</b>'
                        '\n\n🔎 Попробуйте изменить параметры поиска.'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.gender_search
            ))


# Пагинация списка пользователей

@ router.callback_query(
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

        # для избежания ошибки UnboundLocalError если страницы кончились
        page = page_num

        # кнопки "вперед" и "назад" с сообщениями о начале и окончании списка
        if callback_data.action == 'prev':

            if page_num == 0:
                text_prev = '<b>Вы в начале списка</b>'
                await attention_message(callback.message, text_prev, 1)
            else:
                page = max(page_num - 1, 0)

        elif callback_data.action == 'next':

            if page_num + 1 < len(data):  # Проверяем, есть ли следующая страница
                page = page_num + 1
            else:
                text_next = ('<b>Анкеты закончились</b>😔 \nПопробуйте изменить '
                             'параметры поиска, чтобы найти больше пользователей.')
                await attention_message(callback.message, text_next, 3)
        else:
            page = page_num

        # нажатие на кнопку "Назад"
        if callback_data.action == 'menu':

            # Выход из пагинации (четвертый параметр - текст под инфой пользователя (не обязательный))
            await back_callback(callback.message, user_tg_id, 'users_menu')

        # лайк карточки пользователя
        elif callback_data.action == 'like':

            current_user_id = data[page][0]

            # ЗАВЕСТИ ПРОВЕРКУ ЕСЛИ ЕСТЬ В ВХОДЯЩИХ

            # добавление записи в бд
            await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)

            # поверка наличи ответных записей в userreactions
            check = await asyncio.to_thread(check_matches_two_users, user_tg_id, current_user_id)

            # если запись есть
            if check:

                # удаляем записи из userreactions и переносим в matchreactions
                await asyncio.to_thread(delete_and_insert_reactions, user_tg_id, current_user_id)

                # функция отправки сообщения обоим пользователям
                await bot_send_message_matchs_likes(user_tg_id, current_user_id, bot, callback)

            # если нет входящей реакции от пользователя
            if not check:

                # отправляем уведомление пользователю
                await bot_send_message_about_like(user_tg_id, current_user_id, bot)

                # всплывающее уведомление для "меня"
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
'''
