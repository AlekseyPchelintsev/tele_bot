import asyncio
import logging
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.modules.delete_messages import del_last_message
from src.modules.loader import loader
from src.database.requests.city_data import change_city
from src.handlers.edit_name import check_emodji
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_city = State()


delete_messages = []
delete_last_message = []


# Редактировать город


@router.callback_query(F.data == 'edit_city')
async def edit_city(callback: CallbackQuery, state: FSMContext):

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
                'Отправьте название города в чат.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.change_city)


@router.message(Registration.change_city)
async def new_city(message: Message, state: FSMContext, bot: Bot):

    await del_last_message(message)
    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    if message.content_type == 'text' and len(message.text) < 25:
        new_city_name = message.text.title()
        emodji_checked = await check_emodji(new_city_name)
        if not emodji_checked:
            await wrong_city_name(user_tg_id, message_id, bot)
            return
        await change_city_name(user_tg_id, message, message_id, new_city_name, bot)
        await state.clear()
    else:
        await wrong_city_name(user_tg_id, message_id, bot)
        return

        # Логика изменения города


async def wrong_city_name(user_tg_id, message_id, bot):

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
        ),
        reply_markup=kb.back
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
                '❌ Название города должно содержать только текст, не должно содержать эмодзи '
                'и изображения, а так же не должно превышать длинну в <b>25 символов</b>.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


async def change_city_name(user_tg_id, message, message_id, new_city_name, bot):

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
    await asyncio.to_thread(change_city, new_city_name, user_tg_id)

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
                'Город успешно изменен ✅'
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
