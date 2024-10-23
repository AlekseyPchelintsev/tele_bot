import asyncio
from datetime import datetime
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.modules.delete_messages import del_last_message
from src.database.requests.age_change import change_user_age
from src.modules.check_emoji import check_emoji
from src.modules.notifications import loader
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_age = State()


# СТРАНИЦА ИЗМЕНЕНИЯ ДАТЫ РОЖДЕНИЯ

@router.callback_query(F.data == 'edit_age')
async def edit_age_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (на всякий случай)
    await state.clear()

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий возраст:</b> {self_data[0][4]}'
                '\n\n💬 <i>Пришлите в чат дату вашего рождения в формате</i> <b>"ДД.ММ.ГГГГ":</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    # добавляю id сообщения для дальнейшего редактирования
    await state.update_data(message_id=edit_message.message_id)

    # устанавливаю состояние ожидания сообщения с датой рождения
    await state.set_state(Registration.change_age)


# ОЖИДАНИЕ СООБЩЕНИЯ С ДАТОЙ ОТ ПОЛЬЗОВАТЕЛЯ

@router.message(Registration.change_age)
async def edit_age(message: Message, state: FSMContext, bot: Bot):

    # плучаю свой id
    user_tg_id = message.from_user.id

    # плучаю данные отправленные пользователем (ДД.ММ.ГГГГ)
    age = message.text

    # получаю id сообщения для редактирования
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # удаляю сообщение пользователя с датой из чата
    await del_last_message(message)

    # передаю данные сообщения (новой даты рождения) для обработки
    await change_age(user_tg_id, age, message, message_id, state, bot)


# ЛОГИКА ИЗМЕНЕНИЯ ВОЗВРАСТА

async def change_age(user_tg_id, age, message, message_id, state, bot):

    # проверяю является ли сообщение текстом
    if message.content_type == 'text' and message.text:

        # сообщение от пользователя если прошло проверку на текст
        age = message.text

        # проверяю не содержит ли сообщение эмодзи
        emodji_checked = await check_emoji(age)

        # если содержит эмодзи
        if not emodji_checked:

            # вывожу ошибку
            await wrong_date_format(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания нового сообщения
            return

        # если не содержит эмодзи -
        # проверяю соответствие формата присланных данных
        # (ДД.ММ.ГГГГ) и реальность даты
        try:
            check_birth_date = datetime.strptime(age, '%d.%m.%Y')
            user_birth_date = check_birth_date.strftime('%d.%m.%Y')
            today_date = datetime.today()
            user_age = today_date.year - check_birth_date.year - (
                (today_date.month, today_date.day) <
                (check_birth_date.month, check_birth_date.day)
            )

        # если формат не соответствует (ДД.ММ.ГГГГ)
        except ValueError:

            # если неверный формат вывожу уведомление
            await wrong_date_format(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания сообщения с датой (ДД.ММ.ГГГГ)
            return

        # если все проверки прошли - отправляю данные для дальнейшей обработки
        await date_changed(user_tg_id, message, user_age,
                           user_birth_date, message_id,
                           state, bot)

    # если входящее сообщение не является текстом (фото, анимации и т.д.)
    else:

        # вывожу уведомление
        await wrong_date_format(user_tg_id, message_id, bot)

        # возвращаюсь в состояние ожидания сообщения с датой (ДД.ММ.ГГГГ)
        return


# ОШИБКА ФОРМАТА ДАННЫХ ДАТЫ РОЖДЕНИЯ

async def wrong_date_format(user_tg_id, message_id, bot):

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
                f'\n<b>Ваш текущий возраст:</b> {self_data[0][4]}'
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
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш текущий возраст:</b> {self_data[0][4]}'
                '\n\n💬 <i>Пришлите в чат дату вашего рождения в формате</i> <b>"ДД.ММ.ГГГГ":</b>'
                '\n(<code>Пример:</code> <b>01.01.2000</b>)'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# ИЗМЕНЕНИЕ ДАТЫ РОЖДЕНИЯ (ВНЕСЕНИЕ ИЗМЕНЕНИЙ В БД) И ОТРИСОВКА СТРАНИЦЫ

async def date_changed(user_tg_id, message, user_age, user_birth_date, message_id, state, bot):

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
                f'\n<b>Ваш текущий возраст:</b> {self_data[0][4]}'
            ),
            parse_mode='HTML'
        )
    )
    await loader(message, 'Вношу изменения')

    # внесение изменений в бд
    await asyncio.to_thread(change_user_age, user_tg_id, user_age, user_birth_date)

    # получаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']

    # отрисовка страницы с учетом внесенных изменений
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваш возраст:</b> {self_data[0][4]}'
                '\n\nДата рождения успешно изменена ✅'
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

    # удаляю состояние и данные из состояния
    await state.clear()
