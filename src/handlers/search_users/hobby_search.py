import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import hobby_search
from src.handlers.search_users.all_users_search import search_all_users
from src.modules.pagination_logic import (load_bot_pagination_start_or_end_data,
                                          load_pagination_start_or_end_data)

from src.modules.delete_messages import del_last_message
from src.modules.check_emoji import check_emoji, check_markdown_hobbies
from src.database.requests.search_users import (get_stemmed_hobbies_list,
                                                check_users_by_hobbies,
                                                search_users)

from src.handlers.search_users.error_handlers_search import wrong_search_hobby_name

import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# ================================
# ПОИСК ЛЮДЕЙ ПО ХОББИ           |
# ================================


async def search_users_by_hobby(callback, state):

    print(f'ЗАГРУЖЕНО МЕНЮ ПОИСК ПО ХОББИ')

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{hobby_search}',
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

    # сохраняю данные варианта поиска по хобби
    search_data = callback.data

    # получаю данные пола из состояния
    data_state = await state.get_data()
    gender_data = data_state.get('type_of_gender')
    city_data = data_state.get('city_users')

    if search_data == 'my_hobbies':

        print(f'ВЫБРАН ПОИСК ПО МОИМ ХОББИ')
        print(f'ДАННЫЕ В СОСТОЯНИИ - ПОЛ: {gender_data}, ГОРОД: {city_data}')

        # плучаю список своих хобби (прогоняю через стемминг) и удаляю стоп-слова
        my_hobbies_data = await asyncio.to_thread(get_stemmed_hobbies_list, user_tg_id=user_tg_id)

        # если у меня не добавлено ни одного хобби
        if not my_hobbies_data:

            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{hobby_search}',
                        caption=(
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
                    photo=f'{hobby_search}',
                    caption=(
                        '\n\n❌ <b>Список ваших увлечений пуст</b>'
                        '\n\nДобавтье увлечения в настройках профиля или '
                        'попробуйте изменить параметры поиска, например, '
                        'выбрав вариант <b>"Не важно"</b>...'
                        '\n\n📌💬 Вы также можете прислать <b>название увлечения</b> в чат'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.hobbies_search
                )

            # заново устанавливаю состояние ожидания хобби
            await state.set_state(Registration.search_hobby)

        # если у меня есть хотя бы одно хобби
        else:

            # поверяю есть ли хотя бы один пользователь с хобби как у "меня"
            check_users_by_my_hobbies = await asyncio.to_thread(check_users_by_hobbies,
                                                                user_tg_id,
                                                                gender_data,
                                                                city_data,
                                                                my_hobbies_data)

            # если есть хотя бы 1 пользователь с хобби как у меня
            # (с учетом параметров пола и города)
            if check_users_by_my_hobbies:

                # получаю данные всех пользователей
                data = await asyncio.to_thread(search_users,
                                               user_tg_id,
                                               gender_data,
                                               city_data,
                                               my_hobbies_data)

                # получаю длинну списка пользователей для отрисовки кнопок пролистывания
                total_pages = len(data)

                # если найден всего 1 пользователь уведомляю в пагинации
                if total_pages == 1:
                    text_info = '\n\n<b>📍 Найден всего 1 пользователь</b>'
                else:
                    text_info = ''

                # очищаю данные из состояния
                await state.clear()

                # передаю в состояние данные пользователей для пагинации
                await state.update_data(users_data=data)

                # загружаю пагинацию и передаю все данные
                await load_pagination_start_or_end_data(callback.message,
                                                        data,
                                                        'paginator',
                                                        'hobbies_users',
                                                        total_pages,
                                                        text_info)

            # если не найдено ни одного пользователя по моим хобби
            # (с параметрами пола и города)
            else:
                try:
                    await callback.message.edit_media(
                        media=InputMediaPhoto(
                            media=f'{hobby_search}',
                            caption=(
                                '\n\n❌ <b>Пользователи не найдены 😔</b>'
                                '\n\nПопробуйте изменить параметры поиска, например, '
                                'выберите другой <b>город</b> или <b>пол</b>.'
                                '\n\n📌⌨️ Вы также можете выбрать вариант <b>"Не важно"</b>'
                                '\n\n📌💬 или прислать <b>название увлечения</b> в чат'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.hobbies_search
                    )
                except:
                    await callback.message.answer_photo(
                        photo=f'{hobby_search}',
                        caption=(
                            '\n\n❌ <b>Пользователи не найдены 😔</b>'
                            '\n\nПопробуйте изменить параметры поиска, например, '
                            'выберите другой <b>город</b> или <b>пол</b>.'
                            '\n\n📌⌨️ Вы также можете выбрать вариант <b>"Не важно"</b>'
                            '\n\n📌💬 или прислать <b>название увлечения</b> в чат'
                        ),
                        parse_mode='HTML',
                        reply_markup=kb.hobbies_search
                    )
                await state.set_state(Registration.search_hobby)

    # поиск по всем хобби ("Не важно")
    elif search_data == 'all_hobbies':

        print(f'ВЫБРАН ПОИСК ПО ВСЕМ ХОББИ (НЕ ВАЖНО)')

        # присваиваю значение all для логики отбора пользователей из бд
        hobbies_data = ['all']

        # получаю всех пользователей соответствующих параметрам запроса
        # (пола и города)
        data = await asyncio.to_thread(search_users,
                                       user_tg_id,
                                       gender_data,
                                       city_data,
                                       hobbies_data)

        # если пользователи есть
        if data:

            # получаю длинну списка пользователей для отрисовки кнопок пролистывания
            total_pages = len(data)

            # если найден всего 1 пользователь вывожу уведомление
            if total_pages == 1:
                text_info = '\n\n<b>📍 Найден всего 1 пользователь</b>'
            else:
                text_info = ''

            # очищаю из состояния данные для поиска
            await state.clear()

            # добавляю в состояние данные пользователей для пагинации
            await state.update_data(users_data=data)

            # загружаю пагинацию и передаю все данные
            await load_pagination_start_or_end_data(callback.message,
                                                    data,
                                                    'paginator',
                                                    'hobbies_users',
                                                    total_pages,
                                                    text_info)

        # если пользователи не найдены вывожу уведомление
        elif not data:

            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=f'{hobby_search}',
                        caption=(
                            '\n\n❌ <b>Пользователи не найдены 😔</b>'
                            '\n\nПопробуйте изменить параметры поиска, например, '
                            'выберите другой <b>город</b> или <b>пол</b>.'
                        ),
                        parse_mode='HTML'
                    ),
                    reply_markup=kb.hobbies_search
                )
            except:
                await callback.message.answer_photo(
                    photo=f'{hobby_search}',
                    caption=(
                        '\n\n❌ <b>Пользователи не найдены 😔</b>'
                        '\n\nПопробуйте изменить параметры поиска, например, '
                        'выберите другой <b>город</b> или <b>пол</b>.'
                    ),
                    parse_mode='HTML',
                    reply_markup=kb.hobbies_search
                )

            # перехожу в состояние ожидания хобби от пользователя
            await state.set_state(Registration.search_hobby)

        # если во всех этапах поиска выбрано "Не важно"
        elif gender_data == 'all' and city_data == 'all' and hobbies_data == 'all':

            # загружаю всех имеющихся пользователей
            await search_all_users(callback, state, gender_data)


# по конкретному хобби


@router.message(Registration.search_hobby)
async def search_by_hobby(message: Message, state: FSMContext, bot: Bot):

    # удаляю из чата сообщение с присланным хобби
    await del_last_message(message)

    print(f'Я ОТПРАВИЛ ХОББИ В ЧАТ')

    user_tg_id = message.from_user.id

    # получаю данные поиска из состояния
    data_state = await state.get_data()
    gender_data = data_state.get('type_of_gender')
    city_data = data_state.get('city_users')

    # получаю id сообщения для редактирования
    edit_message = await state.get_data()
    message_id = edit_message.get('message_id')

    # проверяю является ли сообщение текстовым
    if message.content_type == 'text':

        # если является - сохраняю в переменную и делаю строчным
        request = message.text.lower()

        # проверка на наличие смайлов в сообщении
        emodji_checked = await check_emoji(request)
        markdown_checked = await check_markdown_hobbies(request)

        if emodji_checked or markdown_checked:
            await wrong_search_hobby_name(user_tg_id, message_id, bot)
            return

        # стемминг запроса и удаление стоп-слов (если есть)
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

        # если есть хотя бы 1 пользователь по моим параметрам поиска
        if check_users_by_my_hobbies:

            # получаю готовый список пользователей
            data = await asyncio.to_thread(search_users,
                                           user_tg_id,
                                           gender_data,
                                           city_data,
                                           stemmed_words)

            # очищаю данные поиска из состояния
            await state.clear()

            # сохраняю данные найденных пользователей в состоянии
            await state.update_data(users_data=data)

            # получаю длинну списка пользователей для правильно отрисовки кнопок переключения
            total_pages = len(data)

            # вывожу уведомление если найден всего 1 пользователь
            if total_pages == 1:
                text_info = '\n\n<b>📍 Найден всего 1 пользователь</b>'
            else:
                text_info = ''

            # загружаю пагинацию и передаю в нее данные
            await load_bot_pagination_start_or_end_data(bot,
                                                        user_tg_id,
                                                        message_id,
                                                        data,
                                                        'paginator',
                                                        'hobbies_users',
                                                        total_pages,
                                                        text_info=text_info)

        # если совпадений по искомому хобби не найдено
        else:

            print(f'СРАБОТАЛО УСЛОВИЕ ЕСЛИ НЕТ СОВПАДЕНИЙ ПО ХОББИ: '
                  f'{stemmed_words}')

            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{hobby_search}',
                    caption=(
                        '\n\n❌ <b>Пользователи не найдены</b> 😔'
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
