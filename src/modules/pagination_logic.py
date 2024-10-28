from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from config import reactions_menu_logo
from config import in_progress, search_menu
from aiogram.types import InputMediaPhoto
from src.modules import keyboard as kb

# если бот ушел в ребут во время открытой пагинации у пользователя


async def no_data_after_reboot_bot_reactions(callback, keyboard_name):

    keyboard = getattr(kb, keyboard_name, None)

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{in_progress}',
                caption=('<b>Что-то пошло не так :(</b> \n\n'
                         '<b>Попробуйте пожалуйста позже.</b>'
                         ),
                parse_mode='HTML'
            ),
            reply_markup=keyboard
        )
    except:
        await callback.message.answer_photo(photo=f'{in_progress}',
                                            caption=('<b>Что-то пошло не так :(</b> \n\n'
                                                     '<b>Попробуйте пожалуйста позже.</b>'),
                                            parse_mode='HTML',
                                            reply_markup=keyboard)


# выход из пагинации и уведомление если список пользователей пуст


async def back_callback(callback_data, keyboard_name, check_data_loading='', text_info=''):

    keyboard = getattr(kb, keyboard_name, None)

    if check_data_loading == 'search':

        photo_data = search_menu

    elif check_data_loading == 'reactions':

        photo_data = reactions_menu_logo

    try:

        await callback_data.edit_media(
            media=InputMediaPhoto(
                media=f'{photo_data}',
                caption=(
                    f'{text_info}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=keyboard
        )

    except:

        await callback_data.answer_photo(
            photo=f'{photo_data}',
            caption=(
                f'{text_info}'
            ),
            parse_mode='HTML',
            reply_markup=keyboard
        )


# загрузка пагинации из оработчика callback

'''
# загрузка пагинации для конца/начала списка (разная клавиатура) и если 1 запись
async def load_pagination_start_or_end_data(callback_data,
                                            data,
                                            keyboard_name,
                                            list_type,
                                            total_pages,
                                            text_info='',
                                            page=0):

    keyboard = getattr(kb, keyboard_name, None)

    gender = await check_gender(data[page][4])
    hobbies = await hobbies_list(data[page][7])

    if keyboard_name == 'match_reactions_pagination':

        try:

            # получаю ник пользователя для передачи в кнопку "Чат"
            nickname = data[page][3]

            # отрисовка страницы (через редактирование сообщения)
            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'► <b>Имя:</b> {data[page][1]}'
                        f'\n► <b>Возраст:</b> {data[page][5]}'
                        f'\n► <b>Пол:</b> {gender}'
                        f'\n► <b>Город:</b> {data[page][6]}'
                        f'\n► <b>Увлечения:</b> {hobbies}'
                        f'\n► <b>О себе:</b> {data[page][-1]}'
                        f'{text_info}'
                    ),
                    parse_mode='HTML',
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type, nickname=nickname, total_pages=total_pages)
            )

        # если не удается отредактировать
        except:

            # отправляю отдельное сообщение
            await callback_data.answer_photo(
                photo=f'{data[page][2]}',
                caption=(
                    f'► <b>Имя:</b> {data[page][1]}'
                    f'\n► <b>Возраст:</b> {data[page][5]}'
                    f'\n► <b>Пол:</b> {gender}'
                    f'\n► <b>Город:</b> {data[page][6]}'
                    f'\n► <b>Увлечения:</b> {hobbies}'
                    f'\n► <b>О себе:</b> {data[page][-1]}'
                    f'{text_info}'
                ),
                parse_mode='HTML',
                reply_markup=keyboard(
                    page=page, list_type=list_type, nickname=nickname, total_pages=total_pages
                )
            )

    # для всех остальных вариантов поиска
    else:

        try:

            # отрисовка страницы (через редактирование сообщения)
            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'► <b>Имя:</b> {data[page][1]}'
                        f'\n► <b>Возраст:</b> {data[page][5]}'
                        f'\n► <b>Пол:</b> {gender}'
                        f'\n► <b>Город:</b> {data[page][6]}'
                        f'\n► <b>Увлечения:</b> {hobbies}'
                        f'\n► <b>О себе:</b> {data[page][-1]}'
                        f'{text_info}'
                    ),
                    parse_mode='HTML',
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type, total_pages=total_pages)
            )

        # если не удается отредактировать
        except:

            # отправляю отдельное сообщение
            await callback_data.answer_photo(
                photo=f'{data[page][2]}',
                caption=(
                    f'► <b>Имя:</b> {data[page][1]}'
                    f'\n► <b>Возраст:</b> {data[page][5]}'
                    f'\n► <b>Пол:</b> {gender}'
                    f'\n► <b>Город:</b> {data[page][6]}'
                    f'\n► <b>Увлечения:</b> {hobbies}'
                    f'\n► <b>О себе:</b> {data[page][-1]}'
                    f'{text_info}'
                ),
                parse_mode='HTML',
                reply_markup=keyboard(
                    page=page, list_type=list_type, total_pages=total_pages
                )
            )
'''

# загрузка пагинации для конца/начала списка (разная клавиатура) и если 1 запись


async def load_pagination_start_or_end_data(
        callback_data,
        data,
        keyboard_name,
        list_type,
        total_pages,
        text_info='',
        page=0):

    # Получаю клавиатуру по имени
    keyboard = getattr(kb, keyboard_name, None)

    # Извлекаю информацию для текущей страницы
    user_data = data[page]
    user_photo = user_data[2]
    user_name = user_data[1]
    user_age = user_data[5]
    # Функция для преобразования пола
    user_gender = await check_gender(user_data[4])
    user_city = user_data[6]
    # функция для форматирования списка хобби
    user_hobbies = await hobbies_list(user_data[7])
    user_about_me = user_data[8]
    employment = user_data[9][0]
    employment_info = user_data[9][1]

    # Подготовка никнейма пользователя для кнопки "Чат"
    nickname = user_data[3]

    # Формируем caption с данными
    caption = (
        f'{user_gender}'  # пол
        f' • {user_name}'  # имя
        f' • {user_age}'  # возраст
        f' • {user_city}'  # город
        f'\n► <b>{employment}:</b> {employment_info}'
        f'\n► <b>Увлечения:</b> {user_hobbies}'
        f'\n► <b>О себе:</b> {user_about_me}'
        f'{text_info}'

    )

    # Проверка типа клавиатуры
    if keyboard_name == 'match_reactions_pagination':
        try:
            # Попытка редактировать сообщение
            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=user_photo,
                    caption=caption,
                    parse_mode='HTML'
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type, nickname=nickname, total_pages=total_pages
                )
            )
        except:
            # Если не удается отредактировать, отправляем новое сообщение
            await callback_data.answer_photo(
                photo=user_photo,
                caption=caption,
                parse_mode='HTML',
                reply_markup=keyboard(
                    page=page, list_type=list_type, nickname=nickname, total_pages=total_pages
                )
            )

    else:
        try:
            # Попытка редактировать сообщение для других клавиатур
            await callback_data.edit_media(
                media=InputMediaPhoto(
                    media=user_photo,
                    caption=caption,
                    parse_mode='HTML'
                ),
                reply_markup=keyboard(
                    page=page, list_type=list_type, total_pages=total_pages
                )
            )
        except:
            # Если не удается отредактировать, отправляем новое сообщение
            await callback_data.answer_photo(
                photo=user_photo,
                caption=caption,
                parse_mode='HTML',
                reply_markup=keyboard(
                    page=page, list_type=list_type, total_pages=total_pages
                )
            )

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

    # Извлекаю информацию для текущей страницы
    user_data = data[page]
    user_photo = user_data[2]
    user_name = user_data[1]
    user_age = user_data[5]
    # Функция для преобразования пола
    user_gender = await check_gender(user_data[4])
    user_city = user_data[6]
    # функция для форматирования списка хобби
    user_hobbies = await hobbies_list(user_data[7])
    user_about_me = user_data[8]
    employment = user_data[9][0]
    employment_info = user_data[9][1]

    # Формируем caption с данными
    caption = (
        f'{user_gender}'  # пол
        f' • {user_name}'  # имя
        f' • {user_age}'  # возраст
        f' • {user_city}'  # город
        f'\n► <b>{employment}:</b> {employment_info}'
        f'\n► <b>Увлечения:</b> {user_hobbies}'
        f'\n► <b>О себе:</b> {user_about_me}'
        f'{text_info}'

    )

    try:

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=user_photo,
                caption=caption,
                parse_mode='HTML'
            ),
            reply_markup=keyboard(
                page=page, list_type=list_type, total_pages=total_pages
            )
        )
    except Exception as e:
        print(f'{e}')
