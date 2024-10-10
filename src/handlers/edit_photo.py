import asyncio
import logging
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import no_photo_id
from src.modules.notifications import loader
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.modules.delete_messages import del_last_message
from src.database.requests.photo_data import (update_user_photo,
                                              delete_user_photo)

import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    photo = State()


delete_messages = []
delete_last_message = []

# Меню "редактировать фото"


@router.callback_query(F.data == 'edit_photo')
async def edit_photo_menu(callback: CallbackQuery, state: FSMContext):

    await state.clear()
    await edit_photo_menu(callback)

# Меню загрузки нового фото профиля


@router.callback_query(F.data == 'new_photo')
async def edit_photo(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Город:</b> {data[0][5]}\n'
                f'<b>Увлечения:</b> {hobbies}\n\n\n'
                'Отправьте ваше фото в чат:'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back_to_photo
    )
    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.photo)

# Загрузка нового фото профиля


@router.message(Registration.photo)
async def get_new_photo(message: Message, state: FSMContext, bot: Bot):

    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')
    await del_last_message(message)
    await add_new_photo(user_tg_id, message, message_id, state, bot)


# Удаление фото профиля


@router.callback_query(F.data == 'del_photo')
async def delete_photo(callback: CallbackQuery):

    user_tg_id = callback.from_user.id
    await delete_photo(user_tg_id, callback)


# Логика меню редактирования фото

async def edit_photo_menu(callback):
    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    photo_id = data[0][1]
    if photo_id == no_photo_id:
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
                reply_markup=kb.edit_no_photo
            )
        except:
            try:
                await del_last_message(callback.message)
            except:
                pass
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
                reply_markup=kb.edit_no_photo
            )
    else:
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
                reply_markup=kb.edit_photo
            )
        except:
            try:
                await del_last_message(callback.message)
            except:
                pass
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
                reply_markup=kb.edit_photo
            )

# Логика обновления фото профиля


async def add_new_photo(user_tg_id, message, message_id, state, bot):
    if message.photo:

        data = await asyncio.to_thread(get_user_data, user_tg_id)
        gender = await check_gender(data[0][3])
        hobbies = await hobbies_list(data[1])

        photo_id = message.photo[-1].file_id
        await asyncio.to_thread(update_user_photo, user_tg_id, photo_id)

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                ),
                parse_mode='HTML'
            )
        )

        await loader(message, 'Загружаю')
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    'Фото профиля успешно обновлено ✅'
                ),
                parse_mode='HTML'
            )
        )

        data = await asyncio.to_thread(get_user_data, user_tg_id)
        gender = await check_gender(data[0][3])
        hobbies = await hobbies_list(data[1])
        await asyncio.sleep(1.5)

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    '<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )
        await state.clear()
    else:
        data = await asyncio.to_thread(get_user_data, user_tg_id)
        gender = await check_gender(data[0][3])
        hobbies = await hobbies_list(data[1])

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    '⚠️ Неизвестный формат файла ⚠️'
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
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    'Отправьте фото в формате <b>.jpg .jpeg</b> или <b>.png</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_to_photo
        )

# Логика удаления фото профиля


async def delete_photo(user_tg_id, callback):
    try:
        data = await asyncio.to_thread(get_user_data, user_tg_id)
        gender = await check_gender(data[0][3])
        hobbies = await hobbies_list(data[1])

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                ),
                parse_mode='HTML'
            )
        )
        await loader(callback.message, 'Удаляю')

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    'Фото успешно удалено 🚫'
                ),
                parse_mode='HTML'
            )
        )

        await asyncio.to_thread(delete_user_photo, user_tg_id)
        data = await asyncio.to_thread(get_user_data, user_tg_id)
        gender = await check_gender(data[0][3])
        hobbies = await hobbies_list(data[1])
        await asyncio.sleep(1.5)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[0][5]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    '<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )
    except:
        pass
