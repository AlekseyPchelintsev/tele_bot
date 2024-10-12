import asyncio
import logging
import random
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from config import delete_profile_id
from aiogram.exceptions import TelegramBadRequest
from src.modules.pagination_logic import no_data_after_reboot_bot, back_callback, load_pagination, load_pagination_bot
from src.modules.notifications import (loader,
                                       bot_notification_about_like,
                                       bot_notification_about_dislike,
                                       bot_send_message_about_like,
                                       bot_send_message_matchs_likes)

from src.modules.delete_messages import del_last_message
from src.database.requests.user_data import get_data, get_user_data
from src.modules.get_self_data import get_user_info
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.handlers.edit_name import check_emodji
from src.database.requests.search_users import get_users_in_city, get_users_by_hobby
from src.handlers.edit_hobbies import wrong_search_hobby_name
from src.database.requests.likes_users import (insert_reaction,
                                               delete_and_insert_reactions,
                                               get_liked_users_ids,
                                               check_matches_two_users,
                                               get_ignore_users_ids)
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    search = State()


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


@router.callback_query(F.data.in_(['search_users_in_city', 'search_users_by_hobby', 'all_users']))
async def choise_search_params(callback: CallbackQuery, state: FSMContext):

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
    else:
        gender_data = 'all'

    if search_data == 'search_users_in_city':
        await search_users_in_city(callback, state, gender_data)
    elif search_data == 'search_users_by_hobby':
        await state.update_data(type_of_gender=gender_data)
        await search_users_by_hobby(callback, state)
    elif search_data == 'all_users':
        await search_all_users(callback, state, gender_data)


# Поиск пользователей в городе


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


# Меню поиска пользователей по хобби


async def search_users_by_hobby(callback, state):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                '<b>Пришлите в чат увлечение, по которому вы хотите найти пользователей:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_users
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.search)

# Поиск пользователей по хобби


@router.message(Registration.search)
async def search_users(message: Message, state: FSMContext, bot: Bot):
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
        emodji_checked = await check_emodji(request)
        if not emodji_checked:
            await wrong_search_hobby_name(user_tg_id, message_id, bot)
            return

        ignore_users_ids = await asyncio.to_thread(get_ignore_users_ids, user_tg_id)
        liked_users_ids = await asyncio.to_thread(get_liked_users_ids, user_tg_id)

        # объединяю оба множества
        ignore_list = ignore_users_ids | liked_users_ids

        # получаю готовый список пользователей
        data = await asyncio.to_thread(get_users_by_hobby, request, user_tg_id, gender_data, ignore_list)

        if not data:
            await del_last_message(message)
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        f'\n<b>Имя:</b> {self_data[0][0]}\n'
                        f'<b>Возраст:</b> {self_data[0][4]}\n'
                        f'<b>Пол:</b> {self_gender}\n'
                        f'<b>Город:</b> {self_data[0][5]}\n'
                        f'<b>Увлечения:</b> {self_hobbies}\n\n'
                        '❌ Пользователи с таким увлечением отсутствуют'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.search_users
            )
            await asyncio.sleep(1.5)
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        f'\n<b>Имя:</b> {self_data[0][0]}\n'
                        f'<b>Возраст:</b> {self_data[0][4]}\n'
                        f'<b>Пол:</b> {self_gender}\n'
                        f'<b>Город:</b> {self_data[0][5]}\n'
                        f'<b>Увлечения:</b> {self_hobbies}\n\n'
                        '<b>Пришлите в чат увлечение, по которому вы хотите найти пользователей:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.search_users
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
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}\n\n'
                    '❌ <b>Пользователи не найдены</b>\n'
                    '🔎 Попробуйте изменить параметры поиска.'
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
