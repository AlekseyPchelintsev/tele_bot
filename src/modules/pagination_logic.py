from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.modules.get_self_data import get_user_info
from config import delete_profile_id
from aiogram.types import InputMediaPhoto
from src.modules.notifications import loader
from src.modules import keyboard as kb

# если бот ушел в ребут во время открытой пагинации у пользователя


async def no_data_after_reboot_bot_reactions(callback, keyboard_name):

    keyboard = getattr(kb, keyboard_name, None)

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{delete_profile_id}',
                caption=('<b>Что-то пошло не так :(</b> \n\n'
                         '<b>Попробуйте пожалуйста позже.</b>'
                         ),
                parse_mode='HTML'
            ),
            reply_markup=keyboard
        )
    except:
        await callback.message.answer_photo(photo=f'{delete_profile_id}',
                                            caption=('<b>Что-то пошло не так :(</b> \n\n'
                                                     '<b>Попробуйте пожалуйста позже.</b>'),
                                            parse_mode='HTML',
                                            reply_markup=keyboard)


# выход из пагинации и уведомление если список пользователей пуст


async def back_callback(callback_data, user_tg_id, keyboard_name, text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    try:
        await callback_data.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}\n\n'
                    f'{text_info}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=keyboard
        )
    except:
        await callback_data.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                f'{text_info}'
            ),
            parse_mode='HTML',
            reply_markup=keyboard
        )


# загрузка пагинации из оработчика callback


# загрузка пагинации для конца/начала списка (разная клавиатура) и если 1 запись
async def load_pagination_start_or_end_data(callback_data,
                                            data,
                                            keyboard_name,
                                            list_type,
                                            total_pages,
                                            page=0,
                                            text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    gender = await check_gender(data[page][4])
    hobbies = await hobbies_list(data[page][7])

    try:

        await callback_data.edit_media(
            media=InputMediaPhoto(
                media=f'{data[page][2]}',
                caption=(
                    f'<b>Имя:</b> {data[page][1]}\n'
                    f'<b>Возраст:</b> {data[page][5]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[page][6]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    f'{text_info}'
                ),
                parse_mode='HTML',
            ),
            reply_markup=keyboard(
                page=page, list_type=list_type, total_pages=total_pages)
        )
    except Exception as e:
        # print(f'{e}')
        pass


# загрузка пагинации (для message с передачей bot)
async def load_bot_pagination_start_or_end_data(bot,
                                                user_tg_id,
                                                message_id,
                                                data,
                                                keyboard_name,
                                                list_type,
                                                total_pages,
                                                page=0,
                                                text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    gender = await check_gender(data[page][4])
    hobbies = await hobbies_list(data[page][7])

    try:

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[page][2]}',
                caption=(
                    f'<b>Имя:</b> {data[page][1]}\n'
                    f'<b>Возраст:</b> {data[page][5]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[page][6]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    f'{text_info}'
                ),
                parse_mode='HTML',
            ),
            reply_markup=keyboard(
                page=page, list_type=list_type, total_pages=total_pages)
        )
    except Exception as e:
        print(f'{e}')

# УДАЛИТЬ
'''
async def load_pagination(callback_data, data, keyboard_name, list_type, page=0, text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    gender = await check_gender(data[page][4])
    hobbies = await hobbies_list(data[page][7])

    if keyboard_name == 'match_reactions_pagination':

        try:

            nickname = data[page][3]

            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'<b>Имя:</b> {data[page][1]}\n'
                        f'<b>Возраст:</b> {data[page][5]}\n'
                        f'<b>Пол:</b> {gender}\n'
                        f'<b>Город:</b> {data[page][6]}\n'
                        f'<b>Увлечения:</b> {hobbies}\n\n'
                        f'{text_info}'
                    ),
                    parse_mode='HTML',
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type, nickname=nickname)
            )
        except Exception as e:
            # print(f'{e}')
            pass

    else:
        try:

            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'<b>Имя:</b> {data[page][1]}\n'
                        f'<b>Возраст:</b> {data[page][5]}\n'
                        f'<b>Пол:</b> {gender}\n'
                        f'<b>Город:</b> {data[page][6]}\n'
                        f'<b>Увлечения:</b> {hobbies}\n\n'
                        f'{text_info}'
                    ),
                    parse_mode='HTML',
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type)
            )
        except Exception as e:
            # print(f'{e}')
            pass


# загрузка пагинации из обработчика message
async def load_pagination_bot(bot, user_tg_id, message_id, data, keyboard_name, list_type, page=0, text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    gender = await check_gender(data[page][4])
    hobbies = await hobbies_list(data[page][7])

    try:

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{data[page][2]}',
                caption=(
                    f'<b>Имя:</b> {data[page][1]}\n'
                    f'<b>Возраст:</b> {data[page][5]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Город:</b> {data[page][6]}\n'
                    f'<b>Увлечения:</b> {hobbies}\n\n'
                    f'{text_info}'
                ),
                parse_mode='HTML',
            ),
            reply_markup=keyboard(
                page=page, list_type=list_type)
        )
    except Exception as e:
        print(f'{e}')
'''
