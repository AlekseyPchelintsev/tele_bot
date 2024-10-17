import asyncio
import re
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_self_data
from src.database.requests.name_change import change_user_name
from src.modules.delete_messages import del_last_message
from src.modules.notifications import loader
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_name = State()


@router.callback_query(F.data == 'edit_name')
async def edit_name_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_self_data, user_tg_id)

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {data[0][0]}'
                '\n\n💬 <b>Пришлите в чат новое имя:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )
    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.change_name)


@router.message(Registration.change_name)
async def edit_name(message: Message, state: FSMContext, bot: Bot):

    await del_last_message(message)
    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    if message.content_type == 'text' and len(message.text) < 20:
        user_name = message.text.title()
        emodji_checked = await check_emodji(user_name)
        if not emodji_checked:
            await wrong_name(user_tg_id, message_id, bot)
            return
        await change_name(user_tg_id, message, user_name, message_id, state, bot)
        await state.clear()
    else:
        await wrong_name(user_tg_id, message_id, bot)
        return


# Логика изменения имени

async def wrong_name(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    gender = await check_gender(data[0][3])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {data[0][0]}'
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
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {data[0][0]}'
                '\n\n❌ Имя должно содержать <b>только текст</b>, не должно '
                'содержать эмодзи и изображения, '
                'а так же не должно превышать длинну в <b>20 символов</b>.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


async def change_name(user_tg_id, message, user_name, message_id, state, bot):

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {data[0][0]}'
            ),
            parse_mode='HTML'
        )
    )

    await loader(message, 'Вношу изменения')
    await asyncio.to_thread(change_user_name, user_tg_id, user_name)

    data = await asyncio.to_thread(get_self_data, user_tg_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                f'\n<b>Ваше имя:</b> {data[0][0]}'
                '\n\nИмя успешно изменено ✅'
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


async def check_emodji(user_name):
    check = re.search(r'('
                      r'[\U0001F600-\U0001F64F]|'
                      r'[\U0001F300-\U0001F5FF]|'
                      r'[\U0001F680-\U0001F6FF]|'
                      r'[\U0001F700-\U0001F77F]|'
                      r'[\U0001F800-\U0001F8FF]|'
                      r'[\U0001F900-\U0001F9FF]|'
                      r'[\U0001FA00-\U0001FAFF]|'
                      r'[\U00002700-\U000027BF]'
                      r')', user_name)
    return check is None
