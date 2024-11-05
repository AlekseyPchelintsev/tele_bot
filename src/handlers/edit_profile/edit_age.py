import asyncio
from datetime import datetime
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.modules.delete_messages import del_last_message
from src.database.requests.age_change import change_user_age
from src.modules.check_emoji import check_emoji, check_partial_markdown
from src.modules.moving_through_sections import check_menu_command
from config import exclude_text_message
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
                '\n\n💬 <i>Напишите дату вашего рождения в формате</i> <b>"ДД.ММ.ГГГГ":</b>'
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

    # передаю данные сообщения (новой даты рождения) для обработки
    await change_age(user_tg_id, age, message, message_id, state, bot)


# ЛОГИКА ИЗМЕНЕНИЯ ВОЗВРАСТА
async def change_age(user_tg_id, age, message, message_id, state, bot):

    # проверяю является ли сообщение текстом
    if message.content_type == 'text' and message.text:

        # сообщение от пользователя если прошло проверку на текст
        age = message.text

        if age not in exclude_text_message:

            # удаляю сообщение пользователя с датой из чата
            await del_last_message(message)

            # проверяю не содержит ли сообщение эмодзи
            emodji_checked = await check_emoji(age)
            markdown_checked = await check_partial_markdown(age)

            # если содержит эмодзи
            if emodji_checked or markdown_checked:

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

                if user_age < 0 or user_age > 95:

                    # плучаю свои данные для отрисовки страницы
                    user_info = await get_user_info(user_tg_id)

                    # Извлекаю свои данные для отрисовки страницы
                    self_data = user_info['data']
                    self_photo = self_data[0][1]
                    self_age = self_data[0][4]

                    try:
                        await bot.edit_message_media(
                            chat_id=user_tg_id,
                            message_id=message_id,
                            media=InputMediaPhoto(
                                media=f'{self_photo}',
                                caption=(
                                    f'\n<b>Ваш текущий возраст:</b> {self_age}'
                                    '\n\n⚠️ <b>Ошибка обработки</b> ⚠️'
                                    '\n<u>Ваш возраст должен быть в диапазоне</u> '
                                    '<u>от 0 до 95 лет</u>'
                                    '\n\n❗️ Пришлите действительную дату вашего рождения, '
                                    'соотвутствующую формату: "<b>ДД.ММ.ГГГГ</b>".'
                                    '\n(Пример: 01.01.2001)'
                                ),
                                parse_mode='HTML'
                            ),
                            reply_markup=kb.back
                        )
                    except Exception as e:
                        pass

                    return

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

        # еслии текст содержит команду из клавиатуры
        else:

            # очищаю состояние, орабатываю ее и открываю
            # соответствующий пункт меню
            await check_menu_command(user_tg_id, message, age, state)

    # если входящее сообщение не является текстом (фото, анимации и т.д.)
    else:

        # удаляю сообщение пользователя с датой из чата
        await del_last_message(message)

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
    try:
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Ваш текущий возраст:</b> {self_data[0][4]}'
                    '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                    '\n\n❗️ Сообщение должно содержать <b>только дату</b> и '
                    'соответствовать формату: "<b>ДД.ММ.ГГГГ</b>".'
                    '\n(Пример: 01.01.2001)'
                    '\n\n💬 <b>Напишите дату вашего рождения в чат:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back
        )
    except Exception as e:
        pass


# ИЗМЕНЕНИЕ ДАТЫ РОЖДЕНИЯ (ВНЕСЕНИЕ ИЗМЕНЕНИЙ В БД) И ОТРИСОВКА СТРАНИЦЫ
async def date_changed(user_tg_id, message, user_age, user_birth_date, message_id, state, bot):

    # внесение изменений в бд
    await asyncio.to_thread(change_user_age, user_tg_id, user_age, user_birth_date)

    # получаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_photo = self_data[0][1]
    self_name = self_data[0][0]
    self_age = self_data[0][4]
    self_city = self_data[0][5]
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']
    # учеба/работа
    employment = user_info['employment']
    employment_info = user_info['employment_info']

    # отрисовка страницы с учетом внесенных изменений
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_photo}',
            caption=(
                f'{self_gender}'  # пол
                f' • {self_name}'  # имя
                f' • {self_age}'  # возраст
                f' • {self_city}'  # город
                f'\n► <b>{employment}:</b> {employment_info}'
                f'\n► <b>Увлечения:</b> {self_hobbies}'
                f'\n► <b>О себе:</b> {about_me}'
                '\n\n✅ <i>Дата рождения изменена</i>'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )

    # await notification(message, 'Дата рождения успешно изменена ✅')

    # удаляю состояние и данные из состояния
    await state.clear()
