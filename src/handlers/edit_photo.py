import asyncio
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import no_photo_id
from src.modules.notifications import loader
from src.modules.get_self_data import get_user_info
from src.modules.delete_messages import del_last_message
from src.database.requests.photo_data import (update_user_photo,
                                              delete_user_photo)

import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    new_photo = State()


delete_messages = []
delete_last_message = []


# МЕНЮ "РЕДАКТИРОВАТЬ ФОТО"

@router.callback_query(F.data == 'edit_photo')
async def edit_photo_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (на всякий случай)
    await state.clear()

    # получаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # поверяю не является id фото в базе id изображения удаленного фото
    if self_data[0][1] == no_photo_id:

        try:

            # отрисовка страницы без кнопки "удалить фото"
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        '<b>Выберите действие:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.edit_no_photo
            )

        except:

            await callback.message.answer_photo(
                photo=f'{self_data[0][1]}',
                caption=(
                    '<b>Выберите действие:</b>'
                ),
                parse_mode='HTML',
                reply_markup=kb.edit_no_photo
            )

    # если id фото в базе не равняется id изображения удаленного фото
    else:

        try:

            # отрисовка страницы с кнопкой "удалить фото"
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        '<b>Выберите действие:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.edit_photo
            )

        except:

            await callback.message.answer_photo(
                photo=f'{self_data[0][1]}',
                caption=(
                    '<b>Выберите действие:</b>'
                ),
                parse_mode='HTML',
                reply_markup=kb.edit_photo
            )


# МЕНЮ ЗАГРУЗКИ НОВОГО ФОТО

@router.callback_query(F.data == 'new_photo')
async def edit_photo(callback: CallbackQuery, state: FSMContext):

    # оплучаю свой id
    user_tg_id = callback.from_user.id

    # получаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                '\n\n💬 <b>Отправьте новое фото в чат:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back_to_photo
    )

    # добавление в состояние id сообщения для редактирования
    await state.update_data(message_id=edit_message.message_id)

    # устанавливаю состояние ожидания нового фотого от пользователя
    await state.set_state(Registration.new_photo)


# СОСТОЯНИЕ ОЖИДАНИЯ НОВОГО ФОТО ОТ ПОЛЬЗОВАТЕЛЯ

@router.message(Registration.new_photo)
async def get_new_photo(message: Message, state: FSMContext, bot: Bot):

    # получаю свой id
    user_tg_id = message.from_user.id

    # получаю id сообщения для редактирования из состояни
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # вношу изменения в бд с новым фото анкеты пользователя
    await add_new_photo(user_tg_id, message, message_id, state, bot)


# ОБНОВЛЕНИЕ ФОТО ПРОФИЛЯ (ДОБАВЛЕНИЕ В БД И ОТРИСОВКА СТРАНИЦЫ)

async def add_new_photo(user_tg_id, message, message_id, state, bot):

    # удаляю последнее сообщение пользователя с фото из чата
    await del_last_message(message)

    # если сообщение является фото
    if message.photo:

        # получаю свои данные для отрисовки страницы
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы
        self_data = user_info['data']
        self_gender = user_info['gender']
        self_hobbies = user_info['hobbies']

        # получаю id загруженного изображение ([-1] - лучшее качество)
        photo_id = message.photo[-1].file_id

        # вношу новое фото в бд
        await asyncio.to_thread(update_user_photo, user_tg_id, photo_id)

        # отрисовка страницы
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '📸'
                ),
                parse_mode='HTML'
            )
        )

        await loader(message, 'Загружаю')

        # получаю свои данные для отрисовки страницы с учетом изменений
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы с учетом изменений
        self_data = user_info['data']
        self_gender = user_info['gender']
        self_hobbies = user_info['hobbies']
        about_me = user_info['about_me']

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    'Фото профиля успешно обновлено ✅'
                ),
                parse_mode='HTML'
            )
        )

        await asyncio.sleep(1.5)

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'► <b>Имя:</b> {self_data[0][0]}'
                    f'\n► <b>Возраст:</b> {self_data[0][4]}'
                    f'\n► <b>Пол:</b> {self_gender}'
                    f'\n► <b>Город:</b> {self_data[0][5]}'
                    f'\n► <b>Увлечения:</b> {self_hobbies}'
                    f'\n► <b>О себе:</b> {about_me}'
                    '\n\n<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )

        # очищаю состояние
        await state.clear()

    # если сообщение не содержит фото
    else:

        # получаю свои данные для отрисовки страницы с учетом изменений
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы с учетом изменений
        self_data = user_info['data']

        # отрисовка страницы
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '⚠️ <b>Неверный формат данных</b> ⚠️'
                ),
                parse_mode='HTML'
            )
        )
        await asyncio.sleep(1.5)

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    'Отправьте фото в формате <b>.jpg .jpeg</b> или <b>.png</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_to_photo
        )
        return


# УДАЛЕНИЕ ФОТО ПРОФИЛЯ (УДАЛЕНИЕ ИЗ БД И ОТРИСОВКА СТРАНИЦЫ)

@router.callback_query(F.data == 'del_photo')
async def delete_profile_photo(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    try:

        # получаю свои данные для отрисовки страницы
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы
        self_data = user_info['data']

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '🗑'
                ),
                parse_mode='HTML'
            )
        )

        await loader(callback.message, 'Удаляю')

        # удаление фото из бд и добавление id "заглушки" удаленного фото
        await asyncio.to_thread(delete_user_photo, user_tg_id)

        # получаю свои данные для отрисовки страницы с учетом изменений
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы с учетом изменений
        self_data = user_info['data']
        self_gender = user_info['gender']
        self_hobbies = user_info['hobbies']
        about_me = user_info['about_me']

        # отрисовка страницы с учетом изменений
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    'Фото профиля успешно удалено 🚫'
                ),
                parse_mode='HTML'
            )
        )

        await asyncio.sleep(1.5)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'► <b>Имя:</b> {self_data[0][0]}'
                    f'\n► <b>Возраст:</b> {self_data[0][4]}'
                    f'\n► <b>Пол:</b> {self_gender}'
                    f'\n► <b>Город:</b> {self_data[0][5]}'
                    f'\n► <b>Увлечения:</b> {self_hobbies}'
                    f'\n► <b>О себе:</b> {about_me}'
                    '\n\n<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )
    except:
        pass
