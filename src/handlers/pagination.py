import asyncio
import logging
import random
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from src.modules.loader import loader
from src.modules.delete_messages import del_last_message
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.handlers.edit_name import check_emodji
from src.handlers.edit_hobbies import wrong_search_hobby_name
from src.database.requests.user_data import get_data, get_user_data
from src.database.requests.search_users import (get_users_by_hobby,
                                                get_users_in_city)
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
    await asyncio.sleep(.5)
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
    data = callback.data
    await state.update_data(type_of_search=data)
    user_tg_id = callback.from_user.id
    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])
    await asyncio.sleep(.5)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                'Кого ищем?'
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


async def search_users_in_city(callback, state, gender_type):

    user_tg_id = callback.from_user.id

    data = await asyncio.to_thread(get_users_in_city, user_tg_id, gender_type)
    try:
        random.shuffle(data)  # рандомайзер пользователей для вывода
    except:
        pass

    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

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
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender_search
        )

        await asyncio.sleep(.2)

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
            reply_markup=kb.paginator(list_type='hobbies_users')
        )

        await state.update_data(users_data=data)


# Меню поиска пользователей по хобби


async def search_users_by_hobby(callback, state):
    user_tg_id = callback.from_user.id
    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])
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

    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

    edit_message = await state.get_data()
    message_id = edit_message.get('message_id')

    if message.content_type == 'text':
        request = message.text.lower()
        emodji_checked = await check_emodji(request)
        if not emodji_checked:
            await wrong_search_hobby_name(user_tg_id, message_id, bot)
            return

        data = await asyncio.to_thread(get_users_by_hobby, request, user_tg_id, gender_data)
        try:
            random.shuffle(data)  # рандомайзер пользователей для вывода
        except:
            pass

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
            await loader(message, 'Загружаю')
            gender = await check_gender(data[0][4])
            hobbies = await hobbies_list(data[0][7])
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{data[0][2]}',
                    caption=(
                        f'<b>Имя:</b> {data[0][1]}\n'
                        f'<b>Возраст:</b> {data[0][5]}\n'
                        f'<b>Пол:</b> {gender}\n'
                        f'<b>Город:</b> {data[0][6]}\n'
                        f'<b>Увлечения:</b> {hobbies}'
                    ),
                    parse_mode='HTML',
                ),
                reply_markup=kb.paginator(list_type='hobbies_users')
            )

            await state.update_data(users_data=data)
    else:
        await wrong_search_hobby_name(user_tg_id, message_id, bot)

# Отображение всех пользователей


async def search_all_users(callback, state, gender_data):

    user_tg_id = callback.from_user.id

    data = await asyncio.to_thread(get_data, user_tg_id, gender_data)
    try:
        random.shuffle(data)  # рандомайзер пользователей для вывода
    except:
        pass
    gender = await check_gender(data[0][4])
    hobbies = await hobbies_list(data[0][7])

    await asyncio.sleep(.5)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][2]}',
            caption=(
                f'<b>Имя:</b> {data[0][1]}\n'
                f'<b>Возраст:</b> {data[0][5]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][6]}\n'
                f'<b>Увлечения:</b> {hobbies}'
            ),
            parse_mode='HTML',
        ),
        reply_markup=kb.paginator(list_type='all_users')
    )
    await state.update_data(users_data=data)


# Пагинация списка пользователей

@router.callback_query(
    kb.Pagination.filter(F.action.in_(
        ['prev', 'next', 'menu', 'user_profile']))
)
async def pagination_handler(
    callback: CallbackQuery,
    callback_data: kb.Pagination,
    state: FSMContext,
):
    list_type = callback_data.list_type
    data = (await state.get_data()).get('users_data')
    page_num = int(callback_data.page)
    user_tg_id = callback.message.chat.id
    if callback_data.action == 'prev':
        page = max(page_num - 1, 0)
    elif callback_data.action == 'next':
        page = min(page_num + 1, len(data) - 1)
    else:
        page = page_num

    if callback_data.action == 'menu':
        self_data = await asyncio.to_thread(get_user_data, user_tg_id)
        self_gender = await check_gender(self_data[0][3])
        self_hobbies = await hobbies_list(self_data[1])
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users_menu
        )

    elif callback_data.action == 'user_profile':
        # TODO await open_profile(callback)
        pass
    else:
        with suppress(TelegramBadRequest):
            gender = await check_gender(data[page][4])
            hobbies = await hobbies_list(data[page][7])
            await callback.message.edit_media(  # Редактирование пагинации
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'<b>Имя:</b> {data[page][1]}\n'
                        f'<b>Возраст:</b> {data[page][5]}\n'
                        f'<b>Пол:</b> {gender}\n'
                        f'<b>Город:</b> {data[page][6]}\n'
                        f'<b>Увлечения:</b> {hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.paginator(page, list_type)
            )

    await callback.answer()


# TODO Просмотр карточки пользователя


'''@router.callback_query(F.data == 'user_profile')
async def open_profile(callback: CallbackQuery):
    await del_last_message(callback.message)
    await notification(callback.message, '🚧 Ведутся работы')
    await search_all_users(callback)'''
