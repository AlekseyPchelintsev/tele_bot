import asyncio
from aiogram.types import InputMediaPhoto
from src.database.requests.user_data import get_user_data
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list

import src.modules.keyboard as kb


async def loader(message, text):
    response_message = await message.answer(f'{text}')
    for i in range(1, 4):
        await response_message.edit_text(f'{text} {"○" * i}', parse_mode='HTML')
        await asyncio.sleep(.1)
    for i in range(1, 4):
        symbols = '●' * i + '○' * (3 - i)
        await response_message.edit_text(f'{text} {symbols}', parse_mode='HTML')
        await asyncio.sleep(.1)
    await asyncio.sleep(.3)
    '''try:
        await message.delete()
    except:
        pass'''
    await response_message.delete()


async def notification(message, text):
    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(2)
    await temporary_message.delete()
    try:
        await message.delete()
    except:
        pass


async def attention_message(message, text):
    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(3)
    try:
        await message.delete()
    except:
        pass
    await temporary_message.delete()

# Всплывающее уведомление при выборе "Решу позже" на входящее уведомление о лайке


async def notification_to_late_incoming_reaction(message, user_tg_id):
    temporary_message = await message.answer('Пользователь добавлен в раздел\n"➡️ <b>Входящие запросы</b>"',
                                             parse_mode='HTML')
    await asyncio.sleep(3)
    await temporary_message.delete()

    try:
        self_data = await asyncio.to_thread(get_user_data, user_tg_id)
        self_gender = await check_gender(self_data[0][3])
        self_hobbies = await hobbies_list(self_data[1])

        await message.edit_media(media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}'
            ),
            parse_mode='HTML'
        ),
            reply_markup=kb.users
        )

    except:
        await message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.users
        )


# Всплывающее сообщение об отправке реакции


async def bot_notification_about_like(message, name):
    temporary_message = await message.answer('📬 Реакция отправлена пользователю '
                                             f'<b>{name}</b>.',
                                             parse_mode='HTML')
    await asyncio.sleep(2)
    await temporary_message.delete()

# Всплывающее сообщение об отмене реакции


async def bot_notification_about_dislike(message, text):
    temporary_message = await message.answer(f'{text}', parse_mode='HTML')
    await asyncio.sleep(2)
    await temporary_message.delete()

# Отправка сообщения пользователю, которого "лайкнули"


async def bot_send_message_about_like(user_tg_id, current_user_id, bot):

    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

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


async def bot_send_message_matchs_likes(user_tg_id, current_user_id, bot, callback):

    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    current_user_data = await asyncio.to_thread(get_user_data, current_user_id)

    self_nickname = self_data[0][2]
    current_user_nickname = current_user_data[0][2]

    # Сообщения с данными для приватной беседы для каждого пользователя

    # сообщение тому, КОМУ ОТВЕТИЛИ на реакцию

    try:
        await bot.edit_message_media(
            chat_id=current_user_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    'Хорошие новости! 🎉\n'
                    f'Пользователь {self_data[0][0]} ответил на вашу '
                    'реакцию и был добавлен в раздел '
                    '<b>"Мои контакты"</b>\n\n'
                    '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.match_reactions(current_user_nickname)
        )

    except:

        try:
            await callback.message.delete()
        except:
            pass

        await bot.send_photo(chat_id=current_user_id,
                             photo=f'{self_data[0][1]}',
                             caption=(
                                 'Хорошие новости! 🎉\n'
                                 f'Пользователь {
                                     self_data[0][0]} ответил на вашу '
                                 'реакцию и был добавлен в раздел '
                                 '<b>"Мои контакты"</b>\n\n'
                                 '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                             ),
                             parse_mode='HTML',
                             reply_markup=kb.match_reactions(self_nickname))

    # сообщение тому, кто лайкнул в ответ (мне)
    try:

        await bot.edit_message_media(
            chat_id=user_tg_id,
            media=InputMediaPhoto(
                media=f'{current_user_data[0][1]}',
                caption=(
                    f'Пользователь {current_user_data[0][0]} '
                    'добавлен в раздел <b>"Мои контакты"</b>\n\n'
                    '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.match_reactions(current_user_nickname)
        )

    except:

        try:
            await callback.message.delete()
        except:
            pass

        await bot.send_photo(chat_id=user_tg_id,
                             photo=f'{current_user_data[0][1]}',
                             caption=(
                                 f'Пользователь {current_user_data[0][0]} '
                                 'добавлен в раздел <b>"Мои контакты"</b>\n\n'
                                 '✉️ <i>Теперь вы можете начать личную беседу.</i>'
                             ),
                             parse_mode='HTML',
                             reply_markup=kb.match_reactions(current_user_nickname))
