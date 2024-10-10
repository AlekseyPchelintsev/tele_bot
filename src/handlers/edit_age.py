import asyncio
import logging
from datetime import datetime
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.modules.delete_messages import del_last_message
from src.database.requests.age_change import change_user_age
from src.handlers.edit_name import check_emodji
from src.modules.notifications import loader
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_age = State()


@router.callback_query(F.data == 'edit_age')
async def edit_age_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
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
                f'<b>Увлечения:</b> {hobbies}\n\n'
                'Пришлите в чат дату вашего рождения в формате <b>"ДД.ММ.ГГГГ":</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )
    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.change_age)


@router.message(Registration.change_age)
async def edit_age(message: Message, state: FSMContext, bot: Bot):

    age = message.text
    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')
    await del_last_message(message)
    await change_age(user_tg_id, age, message, message_id, state, bot)


# Логика изменения возраста

async def change_age(user_tg_id, age, message, message_id, state, bot):

    if message.content_type == 'text' and message.text:
        age = message.text
        emodji_checked = await check_emodji(age)

        if not emodji_checked:
            await wrong_date_format(user_tg_id, message_id, bot)
            return

        try:
            check_birth_date = datetime.strptime(age, '%d.%m.%Y')
            user_birth_date = check_birth_date.strftime('%d.%m.%Y')
            today_date = datetime.today()
            user_age = today_date.year - check_birth_date.year - (
                (today_date.month, today_date.day) <
                (check_birth_date.month, check_birth_date.day)
            )

        except ValueError:
            # Ввели не верный формат
            await wrong_date_format(user_tg_id, message_id, bot)
            return

        await date_changed(user_tg_id, message, user_age,
                           user_birth_date, message_id,
                           state, bot)
        await state.clear()
    else:
        await wrong_date_format(user_tg_id, message_id, bot)
        return


async def wrong_date_format(user_tg_id, message_id, bot):

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
                '⚠️ Неверный формат данных ⚠️'
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
                'Пришлите в чат дату вашего рождения в формате <b>"ДД.ММ.ГГГГ"</b> '
                '(пример: <b>01.01.2000</b>)'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


async def date_changed(user_tg_id, message, user_age, user_birth_date, message_id, state, bot):

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
            ),
            parse_mode='HTML'
        )
    )
    await loader(message, 'Вношу изменения')
    await asyncio.to_thread(change_user_age, user_tg_id, user_age, user_birth_date)
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
                'Дата рождения успешно изменена ✅'
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
                '<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )
    await state.clear()
