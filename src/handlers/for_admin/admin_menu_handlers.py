import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from src.modules.delete_messages import del_last_message
from src.database.requests.admin_requests.ban_and_unban_users import ban_user, unban_user

import src.handlers.for_admin.admin_keyboards as kb_admin
from config import admin_menu_image, ban_user_image, unban_user_image, ban_info_chat_id


router = Router()


class Registration(StatesGroup):
    ban = State()
    unban = State()


# главное меню администратора через сообщение
@router.message(Command('startadmin'), flags={"check_admin": True})
async def admin_menu(message: Message, state: FSMContext):

    await state.clear()

    await message.answer_photo(
        photo=admin_menu_image,
        caption='<b>Панель администратора:</b>',
        parse_mode='HTML',
        reply_markup=kb_admin.admin_keyboard)


# главное меню администратора через колбэк
@router.callback_query(F.data == 'admin_main_menu')
async def admin_menu(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=admin_menu_image,
            caption='<b>Панель администратора:</b>',
            parse_mode='HTML'),
        reply_markup=kb_admin.admin_keyboard)


@router.callback_query(F.data == 'ban_user')
async def add_user_from_ban_list(callback: CallbackQuery, state: FSMContext):

    message_to_edit = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=admin_menu_image,
            caption='<b>Пришли id пользователя для блокировки:</b>',
            parse_mode='HTML'
        ),
        reply_markup=kb_admin.admin_keyboard_back
    )

    await state.update_data(message_to_edit=message_to_edit.message_id)
    await state.set_state(Registration.ban)


@router.message(Registration.ban)
async def get_id_user_for_ban(message: Message, state: State, bot: Bot):

    await del_last_message(message)

    user_tg_id = message.from_user.id
    user_tg_id_for_ban = message.text
    await asyncio.to_thread(ban_user, user_tg_id_for_ban)

    message_data = await state.get_data()
    message_id = message_data.get('message_to_edit')

    # отправляю уведомление пользователю о блокировке профиля
    await bot.send_photo(
        chat_id=user_tg_id_for_ban,
        photo=ban_user_image,
        caption=('<b>Ваш профиль был заблокирован администратором</b> '
                 'в связи с нарушением правил использования сервиса'),
        parse_mode='HTML')

    # отправляю сообщение в чат администраторов
    await bot.send_message(
        chat_id=ban_info_chat_id,
        text=f'🔴 Пользователь с id: {user_tg_id_for_ban} - ЗАБЛОКИРОВАН')

    # редактирую сообщение для возврата в главное меню админа
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=admin_menu_image,
            caption='<b>Панель администратора:</b>',
            parse_mode='HTML'
        ),
        reply_markup=kb_admin.admin_keyboard)

    await state.clear()


@router.callback_query(F.data == 'unban_user')
async def remove_user_from_ban_list(callback: CallbackQuery, state: FSMContext):

    message_to_edit = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=admin_menu_image,
            caption='<b>Пришли id пользователя для снятия блокировки:</b>',
            parse_mode='HTML'
        ),
        reply_markup=kb_admin.admin_keyboard_back
    )

    await state.update_data(message_to_edit=message_to_edit.message_id)
    await state.set_state(Registration.unban)


@router.message(Registration.unban)
async def get_id_user_for_unban(message: Message, state: State, bot: Bot):

    await del_last_message(message)

    user_tg_id = message.from_user.id
    user_tg_id_unban = message.text
    await asyncio.to_thread(unban_user, user_tg_id_unban)

    message_data = await state.get_data()
    message_id = message_data.get('message_to_edit')

    # отправляю уведомление пользователю о снятии блокировки
    await bot.send_photo(
        chat_id=user_tg_id_unban,
        photo=unban_user_image,
        caption=('<b>Ограничения на взаимодействие с </b>'
                 '<b>сервисом сняты админиистратором</b> '),
        parse_mode='HTML')

    # отправляю сообщение в чат админов
    await bot.send_message(
        chat_id=ban_info_chat_id,
        text=f'🟢 Пользователь с id: {user_tg_id_unban} - РАЗБЛОКИРОВАН')

    # редактирую сообщение с возвратом в главное меню админа
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=admin_menu_image,
            caption='<b>Панель администратора:</b>',
            parse_mode='HTML'
        ),
        reply_markup=kb_admin.admin_keyboard)

    await state.clear()
