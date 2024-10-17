import asyncio
import logging
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.notifications import attention_message
from src.modules.delete_messages import del_last_message
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_self_data
from src.database.requests.hobbies_data import check_hobby, delete_hobby
from src.modules.check_gender import check_gender
from src.handlers.edit_name import check_emodji
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    hobby = State()
    hobby_del = State()


delete_messages = []
delete_last_message = []


# проверка наличия хобби и вывод с кнопкой удаления или без

async def check_hobbies_list(user_tg_id, callback):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    if hobbies == '-':
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption='\n<b>Список ваших увлечений пуст 🤷‍♂️</b>',
                    parse_mode='HTML'
                ),
                reply_markup=kb.no_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption='\n<b>Список ваших увлечений пуст 🤷‍♂️</b>',
                parse_mode='HTML',
                reply_markup=kb.no_hobbies)
    else:
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'\n<b>Список ваших увлечений:</b>{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.edit_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.edit_hobbies)


# Редактирование увлечений


@router.callback_query(F.data == 'edit_hobbies')
async def edit_hobbies(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    user_tg_id = callback.from_user.id
    await check_hobbies_list(user_tg_id, callback)

# Меню "добавление хобби"


@router.callback_query(F.data == 'new_hobby')
async def new_hobby(callback: CallbackQuery, state: FSMContext):
    await new_hobby_menu(callback, state)
    await state.update_data(message_id=callback.message.message_id)
    await state.set_state(Registration.hobby)

# Добавление нового хобби


@router.message(Registration.hobby)
async def add_hobby(message: Message, state: FSMContext, bot: Bot):
    await del_last_message(message)

    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    if message.content_type == 'text' and len(message.text) <= 50:
        hobby = message.text.lower()
        emodji_checked = await check_emodji(hobby)

        if not emodji_checked:
            await wrong_hobby_name(user_tg_id, message_id, bot)
            return

        checked = await asyncio.to_thread(check_hobby, user_tg_id, hobby)

        if not checked:
            await hobby_already_exist(user_tg_id, message_id, bot)
            return

        else:
            await hobby_succesful_added(user_tg_id, message_id, bot)

    else:
        await wrong_hobby_name(user_tg_id, message_id, bot)
        return

# Меню удаления хобби


@router.callback_query(F.data == 'del_hobby')
async def del_hobby(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    await check_hobby_to_delete(user_tg_id, callback)

# Удаление хобби


@router.callback_query(F.data.startswith('remove_hobby:'))
async def handle_remove_hobby(callback: CallbackQuery):
    user_tg_id = callback.from_user.id

    # полученный id преобразую в int
    hobby_id = int(callback.data.split(':')[1])

    # удаляю хобби из бд
    await asyncio.to_thread(delete_hobby, user_tg_id, hobby_id)

    # проверяю список хобби пользователя для верной отрисовки на странице
    await check_hobby_to_delete(user_tg_id, callback)
    await attention_message(callback.message, 'Увлечение удалено ✅', 1)


# Логика удаления хобби

async def check_hobby_to_delete(user_tg_id, callback):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies_data = data[1]
    hobbies = await hobbies_list(data[1])

    if hobbies == '-':

        try:

            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption='<b> \nСписок ваших увлечений пуст 🤷‍♂️</b>',
                    parse_mode='HTML'
                ),
                reply_markup=kb.no_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption='<b> \nСписок ваших увлечений пуст 🤷‍♂️</b>',
                parse_mode='HTML',
                reply_markup=kb.no_hobbies)
    else:

        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'\n<b>Список ваших увлечений:</b>{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.delete_hobbies_keyboard(user_tg_id, hobbies_data))

        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.delete_hobbies_keyboard(user_tg_id, hobbies_data))


# Меню добавления хобби

async def new_hobby_menu(callback, state):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{hobbies}'
                    '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                    '\n<b>Одно увлечение - одно сообщение</b>'
                    '\n\n💬 Отправьте увлечение сообщением в чат, '
                    'чтобы я мог его добавить.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_hobbies
        )
    except:
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML',
            reply_markup=kb.back_hobbies
        )

    await state.set_state(Registration.hobby)


# Неверный формат данных

async def wrong_hobby_name(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n❌ Название увлечения должно содержать <b>только текст</b>'
                ', не должно содержать эмодзи и изображения, а так же '
                'не должно превышать длинну в <b>50 символов</b>.'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


async def hobby_already_exist(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n❌ Такое увлечение уже находится в вашем списке'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(2)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# Логика добавления хобби

async def hobby_succesful_added(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n✅ Список ваших увлечений успешно обновлен!'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )
