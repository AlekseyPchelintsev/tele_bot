import asyncio
from config import delete_profile_id
from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from src.modules.get_self_data import get_user_info
from src.database.requests.user_data import get_self_data
from src.modules.notifications import attention_message

from src.database.requests.likes_users import (insert_reaction,
                                               get_reaction,
                                               delete_and_insert_reactions)

import src.modules.keyboard as kb


router = Router()


# Входящие уведомления о реакции


# принимаем реакцию
@router.callback_query(F.data.startswith('accept_request:'))
async def accept_incoming_request_alert(callback: CallbackQuery, bot: Bot):

    user_tg_id = callback.from_user.id
    current_user_id = callback.data.split(':')[1]
    check = await asyncio.to_thread(get_reaction, current_user_id, user_tg_id)

    if check:
        await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)
        # отправка сообщения каждому с данными для приватной беседы
        await bot_send_message_matchs_likes(user_tg_id,
                                            current_user_id,
                                            bot)

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


# Всплывающее уведомление при выборе "Решу позже" на входящее уведомление о лайке
async def notification_to_late_incoming_reaction(message):

    await message.delete()
    await attention_message(message, 'Пользователь добавлен в раздел\n"➡️ <b>Входящие запросы</b>"', 3)


# Всплывающее сообщение об отправке реакции
async def bot_notification_about_like(message):
    temporary_message = await message.answer('📬 Реакция отправлена пользователю',
                                             parse_mode='HTML')
    await asyncio.sleep(1)
    await temporary_message.delete()


# Всплывающее сообщение об отмене реакции (если пользователь ответил взаимно)
async def bot_notification_about_dislike(message, text):
    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(2)
    await temporary_message.delete()


# Отправка сообщения пользователю, которого "лайкнули"
async def bot_send_message_about_like(user_tg_id, current_user_id, bot):

    # плучаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    await bot.send_photo(chat_id=current_user_id,
                         photo=f'{self_data[0][1]}',
                         caption=(
                             '<b>У вас новая реакция от пользователя:</b>\n\n'
                             f'<b>Имя:</b> {self_data[0][0]}\n'
                             f'<b>Возраст:</b> {self_data[0][4]}\n'
                             f'<b>Пол:</b> {self_gender}\n'
                             f'<b>Город:</b> {self_data[0][5]}\n'
                             f'<b>Увлечения:</b> {self_hobbies}'
                         ),
                         parse_mode='HTML',
                         reply_markup=kb.incoming_request_reaction(user_tg_id))


# отправка уведомлений обоим пользователям при взаимной реакции
async def bot_send_message_matchs_likes(user_tg_id, current_user_id, bot):

    self_data = await asyncio.to_thread(get_self_data, user_tg_id)
    current_user_data = await asyncio.to_thread(get_self_data, current_user_id)

    self_nickname = self_data[0][2]
    current_user_nickname = current_user_data[0][2]

    # Сообщения с данными для приватной беседы для каждого пользователя

    # сообщение тому, КОМУ ОТВЕТИЛИ на реакцию

    await bot.send_photo(chat_id=current_user_id,
                         photo=f'{self_data[0][1]}',
                         caption=(
                             'Хорошие новости! 🎉\n'
                             f'Пользователь {self_data[0][0]} ответил '
                             'на вашу реакцию и был добавлен в раздел '
                             '<b>"Мои контакты"</b>\n\n'
                             '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                         ),
                         parse_mode='HTML',
                         reply_markup=kb.match_reactions(self_nickname))

    # сообщение тому, кто лайкнул в ответ (мне)

    await bot.send_photo(chat_id=user_tg_id,
                         photo=f'{current_user_data[0][1]}',
                         caption=(
                             f'Пользователь {current_user_data[0][0]} '
                             'добавлен в раздел <b>"Мои контакты"</b>\n\n'
                             '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                         ),
                         parse_mode='HTML',
                         reply_markup=kb.match_reactions(current_user_nickname))
