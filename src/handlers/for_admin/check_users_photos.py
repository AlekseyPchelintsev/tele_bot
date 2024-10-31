import asyncio
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from src.modules.check_gender import check_gender
from src.modules.get_self_data import get_user_info
from src.database.requests.photo_data import delete_user_photo
from config import admins_chat_id, somthing_wrong

import src.handlers.for_admin.admin_keyboards as kb_admin
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    remove_photo = State()


# проверка фото как нового пользователя, так и
# при изменениий в редактировании профиля
async def check_new_photo_user(photo,
                               gender,
                               name,
                               age,
                               city,
                               new_user_id,
                               bot,
                               info_text=''):

    gender = await check_gender(gender)

    await bot.send_photo(
        chat_id=admins_chat_id,
        photo=photo,
        caption=(
            f'<b>{info_text}</b>'
            f'\n<b>id пльзователя:</b> {new_user_id}'
            f'\n{gender}'  # пол
            f' • {name}'  # имя
            f' • {age}'  # возраст
            f' • {city}'  # город
        ),
        parse_mode='HTML',
        reply_markup=kb_admin.check_photo(new_user_id)
    )


# если фото не прошло модерацию
# (как при регистрации, так и при изменении в редактировании ипрофиля)
@router.callback_query(F.data.startswith('delete_user_photo:'))
async def delete_photo_new_user(callback: CallbackQuery, bot: Bot):

    # плучаю id пльзователя
    new_user_id = callback.data.split(':')[1]

    # получаю фото пользователя перед его удалением,
    # для сохранения данных в ленте канала админов
    user_info = await get_user_info(new_user_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    user_data = user_info['data']
    user_gender = user_info['gender']
    user_photo = user_data[0][1]
    user_name = user_data[0][0]
    user_age = user_data[0][4]
    user_city = user_data[0][5]

    # удаляю фото пользователя не прошедшее модерацию
    await asyncio.to_thread(delete_user_photo, new_user_id)

    # редактирую сообщение в чате админов
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=user_photo,
                caption=(
                    '❌ <b>ФОТО ОТКЛОНЕНО</b> ❌'
                    f'\n<b>id пльзователя:</b> {new_user_id}'
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

        await bot.send_photo(
            chat_id=new_user_id,
            photo=somthing_wrong,
            caption=('Похоже ваше фото не прошло модерацию '
                     'и было отклонено администратором. '
                     '\n\n📸 <b>Попробуйте загрузить другое фото</b>'),
            parse_mode='HTML',
            reply_markup=kb.error_add_to_contacts)

    except Exception as e:
        pass
