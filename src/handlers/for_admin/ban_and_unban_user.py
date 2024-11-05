import asyncio
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from src.modules.get_self_data import get_user_info
from config import ban_user_image
from src.database.requests.admin_requests.ban_and_unban_users import ban_user, unban_user
import src.handlers.for_admin.admin_keyboards as kb_admin

router = Router()


class Registration(StatesGroup):
    remove_photo = State()


# удаление и бан пользователя
@router.callback_query(F.data.startswith('send_to_ban:'))
async def ban_user_by_admin_in_chat_photo(callback: CallbackQuery, bot: Bot):

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

    # блокирую бользователя
    await asyncio.to_thread(ban_user, user_tg_id)

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
            # reply_markup=kb_admin.unban_user_keyboard(user_tg_id)
        )
    except Exception as e:
        pass

    # отправляю уведомление пользователю о блокировке профиля
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
