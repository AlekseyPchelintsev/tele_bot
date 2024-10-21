import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.modules.delete_messages import del_last_message
from src.modules.notifications import loader
from src.database.requests.city_data import change_city
from src.handlers.edit_name import check_emodji
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_city = State()


delete_messages = []
delete_last_message = []


# МЕНЮ РЕДАКТИРОВАНИЯ ГОРОДА

@router.callback_query(F.data == 'edit_city')
async def edit_city(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовк страницы
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий город:</b> {self_data[0][5]}'
                '\n\n💬 <b>Отправьте название нового города в чат.</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    # добавляю в состояние id jсобщения для редактирования
    await state.update_data(message_id=edit_message.message_id)

    # запускаю состояние регистрации нового города
    await state.set_state(Registration.change_city)


# СОСТОЯНИЕ ОЖИДАНИЯ СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ С НАЗВАНИЕМ ГОРОДА

@router.message(Registration.change_city)
async def new_city(message: Message, state: FSMContext, bot: Bot):

    # получаю свой id
    user_tg_id = message.from_user.id

    # удаляю сообщение от пользователя из чата (с названием нового города)
    await del_last_message(message)

    # получаю id сообщения для редактирования из состояния
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # проверяю является ли сообщение текстом
    if message.content_type == 'text' and len(message.text) < 25:

        # сообщение от пользователя если прошло проверку на текст
        new_city_name = message.text.title()

        # проверяю не содержит ли сообщение эмодзи
        emodji_checked = await check_emodji(new_city_name)

        # если содержит эмодзи
        if not emodji_checked:

            # вывожу ошибку
            await wrong_city_name(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания нового сообщения
            return

        # если не содержит эмодзи -
        # передаю данные для внесения изменений в бд и отрисовки страницы
        await change_city_name(user_tg_id, message, message_id, new_city_name, bot, state)

    # если входящее сообщение не является текстом (фото, анимации и т.д.)
    else:

        # вывожу уведомление
        await wrong_city_name(user_tg_id, message_id, bot)

        # возвращаюсь в состояние ожидания сообщения с названием города
        return


# НЕВЕРНЫЙ ФОРМАТ ДАННЫХ В НАЗВАНИИ ГОРОДА

async def wrong_city_name(user_tg_id, message_id, bot):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка сообщения
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий город:</b> {self_data[0][5]}'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий город:</b> {self_data[0][5]}'
                '\n\n❌ Название города должно содержать <b>только текст</b>, не должно содержать эмодзи '
                'и изображения, а так же не должно превышать длинну в <b>25 символов</b>.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# ИЗМЕНЕНИЕ НАЗВАНИЯ ГОРОДА(ВНЕСЕНИЕ ИЗМЕНЕНИЙ В БД) И ОТРИСОВКА СТРАНИЦЫ

async def change_city_name(user_tg_id, message, message_id, new_city_name, bot, state):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий город:</b> {self_data[0][5]}'
            ),
            parse_mode='HTML'
        )
    )

    await loader(message, 'Вношу изменения')

    # вношу изменения в бд
    await asyncio.to_thread(change_city, new_city_name, user_tg_id)

    # плучаю свои данные для отрисовки страницы с внесенными изменениями
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с внесенными изменениями
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']

    # отрисовка страницы с новыми данными
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Город:</b> {self_data[0][5]}'
                '\n\nНазвание города успешно изменено ✅'
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
                f'<b>Имя:</b> {self_data[0][0]}'
                f'\n<b>Возраст:</b> {self_data[0][4]}'
                f'\n<b>Пол:</b> {self_gender}'
                f'\n<b>Город:</b> {self_data[0][5]}'
                f'\n\n<b>Увлечения:</b> {self_hobbies}'
                f'\n\n<b>О себе:</b> {about_me}'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )

    await state.clear()
