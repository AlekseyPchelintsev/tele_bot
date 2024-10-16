import asyncio
from config import delete_profile_id
from aiogram import Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from src.modules.pagination_logic import (no_data_after_reboot_bot_reactions,
                                          back_callback,
                                          load_pagination,
                                          load_pagination_start_or_end_data)

from src.modules.notifications import (bot_notification_about_dislike,
                                       bot_send_message_about_like,
                                       bot_send_message_matchs_likes,
                                       notification_to_late_incoming_reaction)

from src.modules.get_self_data import get_user_info
from src.database.requests.likes_users import (insert_reaction,
                                               get_reaction,
                                               delete_reaction,
                                               get_users_with_likes,
                                               get_users_who_liked_me,
                                               delete_and_insert_reactions,
                                               get_matches_users_data,
                                               send_user_to_ignore_table,
                                               delete_from_my_contacts,
                                               get_my_ignore_list_users,
                                               remove_user_from_ignore_table)

import src.modules.keyboard as kb


router = Router()


# презагрузка пагинации после лайка/дизлайка/удаления из контактов/удадения из игнора
async def reload_reaction_pagination_after_hide_or_like(callback,
                                                        user_tg_id,
                                                        data,
                                                        keyboard,
                                                        list_type,
                                                        page):

    # удаляем пользователя из data
    data.pop(page)

    # если False (data пустая)
    if not data:

        # выводим сообщение об отсутствии пользователей
        text_info = '<b>Список пользователей пуст</b> 🤷‍♂️'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            text_info)

    # если True (data не пустая)
    else:
        total_pages = len(data)
        # Обновляем номер страницы
        if page >= len(data):

            # Переход на последнюю страницу, если текущая выходит за пределы
            page = len(data) - 1

            # отрисовываю клавиатуру с учетом изменений
        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                keyboard,
                                                list_type,
                                                total_pages,
                                                page)

'''
# Входящие уведомления о реакции
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


# Меню реакций
@router.callback_query(F.data == 'all_reactions')
async def all_reactions_menu(callback: CallbackQuery):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.reactions
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.reactions
        )



# Мои реакции
@router.callback_query(F.data == 'my_reactions')
async def my_reactions(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_users_with_likes, user_tg_id)

    # если False (данные отсутствуют)
    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>Список реакций пуст</b> 🤷‍♂️'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            text_info)

    # если True (есть данные)
    else:

        total_pages = len(data)

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator_likes',
                                                'my_like_users',
                                                total_pages)

        await state.update_data(users_data=data)



# Входящие реакции
@router.callback_query(F.data == 'incoming_reactions_list')
async def my_reactions(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_users_who_liked_me, user_tg_id)

    # если False (данные отсутствуют)
    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>Входящих реакций пока что нет</b> 😔'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            text_info)

    # если True (есть данные)
    else:

        total_pages = len(data)

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator_likes',
                                                'my_like_users',
                                                total_pages)

        await state.update_data(users_data=data)



# Взаимные реакции (мои контакты)
@router.callback_query(F.data == 'match_reactions_list')
async def my_reactions(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_matches_users_data, user_tg_id)

    # если False (данные отсутствуют)
    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>Список ваших контактов пуст</b> 😔'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            text_info)

    # если True (есть данные)
    else:

        total_pages = len(data)

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator_likes',
                                                'my_like_users',
                                                total_pages)

        await state.update_data(users_data=data)



# меню "скрытые анкеты"
@router.callback_query(F.data == 'ignore_list')
async def ignore_users_list(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id

    data = await asyncio.to_thread(get_my_ignore_list_users, user_tg_id)

    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>У вас нет скрытых пользователей.</b>'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            text_info)

    # если True (есть данные)
    else:
        total_pages = len(data)

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'ignored_users_pagination',
                                                'ignore_users_list',
                                                total_pages)

        await state.update_data(users_data=data)
'''


# Пагинация пользователей в "Мои реакции"
@router.callback_query(
    kb.PaginationLikes.filter(F.action.in_(
        ['prev_likes',
         'next_likes',
         'menu_likes',
         'in_reactions_like',
         'in_reactions_dislike',
         'delete_incoming',
         'delete_contact',
         'remove_from_ignore']))
)
async def pagination_handler_likes(
    callback: CallbackQuery,
    callback_data: kb.PaginationLikes,
    state: FSMContext,
    bot: Bot
):
    user_tg_id = callback.message.chat.id
    list_type = callback_data.list_type

    # проверка list_type для передачи правильной клавиатуры

    if list_type == 'my_like_users':
        keyboard = 'paginator_likes'
    elif list_type == 'incoming_like_users':
        keyboard = 'incoming_reactions'
    elif list_type == 'match_like_users':
        keyboard = 'match_reactions_pagination'
    elif list_type == 'ignore_users_list':
        keyboard = 'ignored_users_pagination'

    # data[0][3] - ник пользователя
    data = (await state.get_data()).get('users_data')

    # если бот ушел в ребут с открытой пагинацией у пользователя
    if not data:
        await no_data_after_reboot_bot_reactions(callback, 'back_reactions')

    # Загрузка пагинации если data не None
    else:

        # длинна data для отрисовки кнопок переключения карточек
        total_pages = len(data)

        page_num = int(callback_data.page)

        if callback_data.action == 'prev_likes':
            page = max(page_num - 1, 0)
        elif callback_data.action == 'next_likes':
            page = min(page_num + 1, len(data) - 1)
        else:
            page = page_num

            # получаем данные текущего пользователя, открытого в пагинации
        current_user_id = data[page][0]

        # нажатие на кнопку "Назад"
        if callback_data.action == 'menu_likes':

            # Выход из пагинации (четвертый параметр - текст под инфой пользователя (не обязательный))
            await back_callback(callback.message, user_tg_id, 'reactions')

            # Блок обрабатывает колбэк "incoming_reactions" / "Входящие запросы"

        # прием запроса в "Входящие реакции"
        elif callback_data.action == 'in_reactions_like':

            check = await asyncio.to_thread(get_reaction, current_user_id, user_tg_id)

            if check:

                # добавление реакции в бд
                await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)

                # удаление взаимных записей из таблицы userreactions и
                # внесение одной записи в таблицу matchreactions
                # благодаря чему пользователь будет отображаться в "Мои контакты"
                await asyncio.to_thread(delete_and_insert_reactions,
                                        user_tg_id,
                                        current_user_id)

                # удаление дизлайкнутого пользователя из data и отрисовка пагинации без него
                await reload_reaction_pagination_after_hide_or_like(callback,
                                                                    user_tg_id,
                                                                    data,
                                                                    keyboard,
                                                                    list_type,
                                                                    page)

                # отправка сообщения каждому с данными для приватной беседы
                await bot_send_message_matchs_likes(user_tg_id, current_user_id, bot, callback)

            else:

                # добавление реакции в бд
                await asyncio.to_thread(insert_reaction, user_tg_id, current_user_id)

                # отправка реакции пользователю
                await bot_send_message_about_like(user_tg_id, current_user_id, bot)

                # удаление пользователя из data и отрисовка пагинации без него
                await reload_reaction_pagination_after_hide_or_like(callback,
                                                                    user_tg_id,
                                                                    data,
                                                                    keyboard,
                                                                    list_type,
                                                                    page)

                # сообщение "мне"
                await callback.message.answer_photo(photo=delete_profile_id,
                                                    caption=(
                                                        '<b>Что-то пошло не так</b> 🫤\n\n'
                                                        '<b>Возможно пользователь передумал и удалил свою реакцию</b> 😔\n\n'
                                                        '<i>Но мы все равно отправили ему вашу 😉</i>'
                                                    ),
                                                    parse_mode='HTML',
                                                    reply_markup=kb.error_add_to_contacts
                                                    )

        # отказ от входящего запроса из "Входящие реакции"
        elif callback_data.action == 'delete_incoming':

            # удаляем реакцию из бд и выводим уведомление
            # передаю id в обратном порядке
            delete = await asyncio.to_thread(delete_reaction, current_user_id, user_tg_id)

            if delete:
                # добавляем пользователя в ignorelist
                await asyncio.to_thread(send_user_to_ignore_table, user_tg_id, current_user_id)

                # удаление дизлайкнутого пользователя из data и отрисовка пагинации без него
                await reload_reaction_pagination_after_hide_or_like(callback,
                                                                    user_tg_id,
                                                                    data,
                                                                    keyboard,
                                                                    list_type,
                                                                    page)

                await bot_notification_about_dislike(callback.message,
                                                     '❗️ <b>Реакция отклонена.</b>\n'
                                                     'Пользователь добавлен в раздел:\n'
                                                     '"🚷 <b>Скрытые пользователи</b>"')

            else:
                await bot_notification_about_dislike(callback.message,
                                                     '🚧 <b>Что-то пошло не так. Попробуйте позже</b> 🚧')

        # отмена моего запроса в "Мои реакции"
        elif callback_data.action == 'in_reactions_dislike':

            # удаляем реакцию из бд
            await asyncio.to_thread(delete_reaction, user_tg_id, current_user_id)

            # удаление дизлайкнутого пользователя из data и отрисовка пагинации без него
            await reload_reaction_pagination_after_hide_or_like(callback,
                                                                user_tg_id,
                                                                data,
                                                                keyboard,
                                                                list_type,
                                                                page)

            await bot_notification_about_dislike(callback.message,
                                                 '🚫 <b>Реакция успешно удалена!</b>')

        # удаление пользователя из "Мои контакты"
        elif callback_data.action == 'delete_contact':

            # удаляем реакцию из бд (matchreactions) и выводим уведомление
            delete = await asyncio.to_thread(delete_from_my_contacts, user_tg_id, current_user_id)

            if delete:
                # добавляем пользователя в ignorelist
                await asyncio.to_thread(send_user_to_ignore_table, user_tg_id, current_user_id)

                # удаление дизлайкнутого пользователя из data и отрисовка пагинации без него
                await reload_reaction_pagination_after_hide_or_like(callback,
                                                                    user_tg_id,
                                                                    data,
                                                                    keyboard,
                                                                    list_type,
                                                                    page)

                await bot_notification_about_dislike(callback.message,
                                                     '❗️ <b>Пользователь удален из ваших контактов</b>\n'
                                                     'и добавлен в раздел:\n'
                                                     '"🚷 <b>Скрытые пользователи</b>"')

            else:
                await bot_notification_about_dislike(callback.message,
                                                     '🚧 Что-то пошло не так. Попробуйте позже 🚧')

        # удаление пользователя из "Скрытые пользователи"
        elif callback_data.action == 'remove_from_ignore':

            # удаляем реакцию из бд (matchreactions) и выводим уведомление
            delete = await asyncio.to_thread(remove_user_from_ignore_table, user_tg_id, current_user_id)

            if delete:

                # удаление пользователя из data и отрисовка пагинации без него
                await reload_reaction_pagination_after_hide_or_like(callback,
                                                                    user_tg_id,
                                                                    data,
                                                                    keyboard,
                                                                    list_type,
                                                                    page)

                await bot_notification_about_dislike(callback.message,
                                                     '☺️ <b>Пользователь снова доступен в поиске!</b>')

            else:
                await bot_notification_about_dislike(callback.message,
                                                     '🚧 <b>Что-то пошло не так. Попробуйте позже</b> 🚧')

        # отрисовка клавиатуры при переключении между карточками
        else:

            await load_pagination_start_or_end_data(callback.message,
                                                    data,
                                                    keyboard,
                                                    list_type,
                                                    total_pages,
                                                    page)

    await callback.answer()
