import asyncio
from config import delete_profile_id
from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from src.modules.notifications import (bot_send_message_about_like,
                                       bot_send_message_matchs_likes,
                                       notification_to_late_incoming_reaction)

from src.database.requests.likes_users import (insert_reaction,
                                               get_reaction,
                                               delete_and_insert_reactions)

import src.modules.keyboard as kb


router = Router()


# Входящие уведомления о реакции


# пинимаем реакцию
@router.callback_query(F.data.startswith('accept_request:'))
async def accept_incoming_request_alert(callback: CallbackQuery, bot: Bot):

    user_tg_id = callback.from_user.id
    current_user_id = callback.data.split(':')[1]
    check = await asyncio.to_thread(get_reaction, current_user_id, user_tg_id)

    if check:
        await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)
        # отправка сообщения каждому с данными для приватной беседы
        await bot_send_message_matchs_likes(user_tg_id, current_user_id, bot, callback)

        # удаление взаимных записей из таблицы userreactions и
        # внесение одной записи в таблицу matchreactions
        # благодаря чему пользователь будет отображаться в "Мои контакты"
        await asyncio.to_thread(delete_and_insert_reactions,
                                user_tg_id,
                                current_user_id)

        await callback.message.delete()

    else:
        await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)
        await bot_send_message_about_like(user_tg_id, current_user_id, bot)
        await callback.message.edit_media(media=InputMediaPhoto(
            media=delete_profile_id,
            caption=(
                '<b>Что-то пошло не так</b> 🫤\n\n'
                '<b>Возможно пользователь передумал и удалил свою реакцию</b> 😔\n\n'
                '<i>Но мы все равно отправили ему вашу 😉</i>'
            ),
            parse_mode='HTML'
        ),
            reply_markup=kb.error_add_to_contacts
        )


# откладываем на потом
@router.callback_query(F.data.startswith('accept_late:'))
async def accept_late_incoming_request_alert(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    current_user_id = callback.data.split(':')[1]
    check = await asyncio.to_thread(get_reaction, current_user_id, user_tg_id)

    if check:
        await notification_to_late_incoming_reaction(callback.message)
    else:
        await callback.message.edit_media(media=InputMediaPhoto(
            media=delete_profile_id,
            caption=(
                '<b>Что-то пошло не так</b> 🫤\n\n'
                '<b>Возможно пользователь случайно отправил вам реакцию\n'
                'и уже удалил ее</b> 🤷‍♂️'
            ),
            parse_mode='HTML'
        ),
            reply_markup=kb.error_add_to_contacts
        )


# закрытие окна уведомления
@router.callback_query(F.data == 'close_notification')
async def close_notice(callback: CallbackQuery):
    await callback.message.delete()
