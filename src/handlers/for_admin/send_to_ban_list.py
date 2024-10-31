import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from src.modules.get_self_data import get_user_info
from aiogram.fsm.context import FSMContext
from config import ban_user_image
from src.database.requests.admin_requests.delete_and_block_profile import (
    delete_and_ban_user,
    check_user_in_ban
)

router = Router()


class Registration(StatesGroup):
    remove_photo = State()


# удаление и бан пользователя
@router.callback_query(F.data.startswith('send_to_ban:'))
async def ban_user(callback: CallbackQuery, bot: Bot):

    # получаю id пользователя
    user_tg_id = callback.data.split(':')[1]

    # получаю данные пользователя перед его удалением,
    # для сохранения данных в ленте канала админов
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    user_data = user_info['data']
    user_gender = user_info['gender']
    user_photo = user_data[0][1]
    user_name = user_data[0][0]
    user_age = user_data[0][4]
    user_city = user_data[0][5]

    # удаляю и блокирую бользователя
    await asyncio.to_thread(delete_and_ban_user, user_tg_id)

    # редактирую сообщение в чате админов
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=user_photo,
                caption=(
                    '🚷 <b>ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН</b> 🚷'
                    f'\n<b>id пльзователя:</b> {user_tg_id}'
                    f'\n{user_gender}'  # пол
                    f' • {user_name}'  # имя
                    f' • {user_age}'  # возраст
                    f' • {user_city}'  # город

                ),
                parse_mode='HTML'
            )
        )
    except Exception as e:
        pass

    # отправляю уведомление пользователю, что фото не прошло модерацию
    try:
        await bot.edit_message_media(
            chat_id=user_tg_id,
            media=InputMediaPhoto(
                media=ban_user_image,
                caption=('<b>Ваш профиль был заблокирован администратором</b> '
                         'в связи с нарушением правил использования сервиса'),
                parse_mode='HTML'))

    except:
        await bot.send_photo(
            chat_id=user_tg_id,
            photo=ban_user_image,
            caption=('<b>Ваш профиль был заблокирован администратором</b> '
                     'в связи с нарушением правил использования сервиса'),
            parse_mode='HTML')


# ПРОВЕРКИ БАНА ПОЛЬЗОВАТЕЛЯ ПРИ ВЗАИИМОДЕЙСТВИИ С БОТОМ
# проверка наличия пользователя в бан листе для callback оработчиков
def check_ban_callback(func):
    async def wrapper(callback: CallbackQuery, state: FSMContext):
        user_tg_id = callback.from_user.id  # Получаем ID пользователя
        if await asyncio.to_thread(check_user_in_ban, user_tg_id):
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=ban_user_image,
                        caption=('<b>Ваш профиль был заблокирован администратором</b> '
                                 'в связи с нарушением правил использования сервиса'),
                        parse_mode='HTML'
                    )
                )
            except:
                await callback.message.answer_photo(
                    photo=ban_user_image,
                    caption=('<b>Ваш профиль был заблокирован администратором</b> '
                             'в связи с нарушением правил использования сервиса'),
                    parse_mode='HTML'
                )
        else:
            # Вызываем оригинальный обработчик
            await func(callback, state)
    return wrapper


# проверка наличия пользователя в бан листе для callback оработчиков (bot)
def check_ban_callback_bot(func):
    async def wrapper(callback: CallbackQuery, state: FSMContext, bot: Bot):
        user_tg_id = callback.from_user.id  # Получаем ID пользователя
        if await asyncio.to_thread(check_user_in_ban, user_tg_id):
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=ban_user_image,
                        caption=('<b>Ваш профиль был заблокирован администратором</b> '
                                 'в связи с нарушением правил использования сервиса'),
                        parse_mode='HTML'
                    )
                )
            except:
                await callback.message.answer_photo(
                    photo=ban_user_image,
                    caption=('<b>Ваш профиль был заблокирован администратором</b> '
                             'в связи с нарушением правил использования сервиса'),
                    parse_mode='HTML'
                )
        else:
            # Вызываем оригинальный обработчик
            await func(callback, state, bot)
    return wrapper


# проверка наличия пользователя в бан листе для message обработчиков
def check_ban_message(func):
    async def wrapper(message: Message, state: FSMContext):
        user_tg_id = message.from_user.id  # Получаем ID пользователя
        if await asyncio.to_thread(check_user_in_ban, user_tg_id):
            try:
                await message.edit_media(
                    media=InputMediaPhoto(
                        media=ban_user_image,
                        caption=('<b>Ваш профиль был заблокирован администратором</b> '
                                 'в связи с нарушением правил использования сервиса'),
                        parse_mode='HTML'
                    )
                )

            except:
                await message.answer_photo(
                    photo=ban_user_image,
                    caption=('<b>Ваш профиль был заблокирован администратором</b> '
                             'в связи с нарушением правил использования сервиса'),
                    parse_mode='HTML'
                )
        else:
            # Вызываем оригинальный обработчик
            await func(message, state)
    return wrapper


# проверка наличия пользователя в бан листе для message обработчиков (bot)
def check_ban_message_bot(func):
    async def wrapper(message: Message, state: FSMContext, bot: Bot):
        user_tg_id = message.from_user.id  # Получаем ID пользователя
        if await asyncio.to_thread(check_user_in_ban, user_tg_id):
            try:
                await message.edit_media(
                    media=InputMediaPhoto(
                        media=ban_user_image,
                        caption=('<b>Ваш профиль был заблокирован администратором</b> '
                                 'в связи с нарушением правил использования сервиса'),
                        parse_mode='HTML'
                    )
                )

            except:
                await message.answer_photo(
                    photo=ban_user_image,
                    caption=('<b>Ваш профиль был заблокирован администратором</b> '
                             'в связи с нарушением правил использования сервиса'),
                    parse_mode='HTML'
                )
        else:
            # Вызываем оригинальный обработчик
            await func(message, state, bot)
    return wrapper
