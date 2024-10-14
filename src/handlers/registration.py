import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.notifications import notification
from config import sucessful_registration, video_no_nickname, in_progress
from src.modules.delete_messages import del_messages, del_last_message
from src.database.requests.photo_data import get_user_photo_id
from src.database.requests.new_user import add_new_user
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    name = State()
    nickname = State()
    photo = State()
    city = State()
    gender = State()
    birth_date = State()


delete_messages = []
delete_last_message = []


@router.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    # контрольно убирает состояния если пользователь
    # попал в это меню после удаления анкеты
    await state.clear()

    user_tg_id = callback.from_user.id
    # user_nickname = callback.from_user.username
    user_nickname = 'kin0govno'
    await del_last_message(callback.message)

    if user_tg_id:
        if user_nickname:

            del_message = await callback.message.answer(text='Пожалуйста, ведите ваше имя:')
            delete_last_message.append(del_message.message_id)
            await state.set_state(Registration.name)

        else:
            await callback.message.answer_video(
                video=video_no_nickname,
                caption=('\n\n⚠️ Чтобы продолжить, вам нужно указать \n<b>"Имя пользователя"</b> '
                         'в настройках вашей учетной записи <b>Telegram</b>.\n\n'
                         'Только после этого вы сможете:'),
                parse_mode='HTML',
                reply_markup=kb.regkey

            )
    else:
        await callback.message.answer_photo(photo=in_progress,
                                            caption=('Что-то пошло не так :( \n'
                                                     'Попробуйте снова чуть позже.'),
                                            parse_mode='HTML',
                                            reply_markup=kb.regkey
                                            )

# Получение данных пользователя и добавление их в бд


@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext, bot: Bot):

    await del_messages(message.chat.id, delete_last_message)
    await message.delete()

    user_tg_id = message.from_user.id
    name = message.text
    name = name.title()
    user_nickname = message.from_user.username
    photo_id = await get_user_photo_id(bot, user_tg_id)

    await state.update_data(name=name, nickname=user_nickname, photo=photo_id)
    # Пол
    await state.set_state(Registration.city)
    await asyncio.sleep(.5)
    del_message = await message.answer(text='Напишите в чат название города, в котором вы проживаете.')
    delete_last_message.append(del_message.message_id)

# Регистрация города


@router.message(Registration.city)
async def get_city(message: Message, state: FSMContext):

    await del_messages(message.chat.id, delete_last_message)
    await del_last_message(message)

    data_city = message.text
    city = data_city.title()
    await state.update_data(city=city)
    await state.set_state(Registration.gender)
    await asyncio.sleep(.3)
    await message.answer(text='Укажите ваш пол.', reply_markup=kb.gender)

    # Регистрация пола


@router.callback_query(Registration.gender, F.data.in_(['male', 'female', 'other']))
async def gender_checked(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    gender = callback.data
    await state.update_data(gender=gender)
    await asyncio.sleep(.3)
    await state.set_state(Registration.birth_date)
    del_message = await callback.message.answer(text='Укажите дату вашего рождения в формате "ДД.ММ.ГГГГ".')
    delete_messages.append(del_message.message_id)

# TODO Регистрация возраста и завершение регистрации


@router.message(Registration.birth_date)
async def age_checked(message: Message, state: FSMContext):
    chat_id = message.chat.id
    delete_messages.append(message.message_id)
    date_input = message.text

    # Обработка даты рождения (вынести в функцию)
    try:
        check_birth_date = datetime.strptime(date_input, '%d.%m.%Y')
        user_birth_date = check_birth_date.strftime('%d.%m.%Y')
        today_date = datetime.today()
        user_age = today_date.year - check_birth_date.year - (
            (today_date.month, today_date.day) <
            (check_birth_date.month, check_birth_date.day)
        )

    except ValueError:
        # Ввели не верный формат
        await del_messages(chat_id, delete_messages)
        await notification(message, '⚠️ Неверный формат данных ⚠️')
        del_message = await message.answer(
            text='Пожалуйста, введите дату вашего рождения в формате "<b>ДД.ММ.ГГГГ</b>".',
            parse_mode='HTML'
        )
        delete_messages.append(del_message.message_id)
        await state.set_state(Registration.birth_date)
        return

    # Извлекаем данные из состояния
    current_datetime = datetime.now()
    user_tg_id = message.from_user.id
    data = await state.get_data()
    name = data.get('name')
    photo_id = data.get('photo')
    nickname = data.get('nickname')
    gender = data.get('gender')
    city = data.get('city')

    # Функция добавления пользоваателя
    await asyncio.to_thread(
        add_new_user, current_datetime, user_tg_id, name, photo_id,
        nickname, gender, user_age, user_birth_date, city
    )

    await state.clear()
    await del_messages(chat_id, delete_messages)
    await message.answer_photo(
        photo=f'{sucessful_registration}',
        caption='<b>Вы успешно зарегистрированы</b> ✅\n\n'
        'Вы также можете рассказать о своих увлечениях людям, '
        'чтобы им было проще вас найти.',
        parse_mode='HTML',
        reply_markup=kb.start_edit
    )
