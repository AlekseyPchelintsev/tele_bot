import asyncio
from config import in_progress
from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.handlers.reactions_menu.notice_reaction import bot_send_message_about_like, bot_notification_about_dislike, bot_send_message_matchs_likes
from src.modules.pagination_logic import (no_data_after_reboot_bot_reactions,
                                          back_callback,
                                          load_pagination_start_or_end_data)

from src.modules.notifications import attention_message

from src.database.requests.user_data import check_user
from src.database.requests.likes_users import (insert_reaction,
                                               get_reaction,
                                               delete_reaction,
                                               delete_and_insert_reactions,
                                               send_user_to_ignore_table,
                                               delete_from_my_contacts,
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
                            'reactions',
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
                                                page=page)


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

    # получаю данные пользователей из состояния
    users_data = await state.get_data()
    data = users_data.get('users_data')

    # если бот ушел в ребут с открытой пагинацией у пользователя и данных нет
    if not data:

        print(f'СРАБОТАЛ БЛОК IF NOT DATA В ПАГИНАЦИИ РЕАКЦИЙ: {data}')
        await no_data_after_reboot_bot_reactions(callback, 'back_reactions')

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
            menu_text = '<b>Раздел ваших реакций:</b>'
            await back_callback(callback.message,
                                user_tg_id,
                                'reactions',
                                'reactions',
                                menu_text)

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
                await bot_send_message_matchs_likes(user_tg_id,
                                                    current_user_id,
                                                    bot)

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
                await callback.message.answer_photo(photo=in_progress,
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

            # вывожу уведомление
            await bot_notification_about_dislike(callback.message,
                                                 '🚫 <b>Реакция успешно удалена!</b>')

        # удаление пользователя из "Мои контакты"
        elif callback_data.action == 'delete_contact':

            # удаляем реакцию из бд (matchreactions) и выводим уведомление
            await asyncio.to_thread(delete_from_my_contacts, user_tg_id, current_user_id)

            # добавляем пользователя в ignorelist
            await asyncio.to_thread(send_user_to_ignore_table, user_tg_id, current_user_id)

            # удаление дизлайкнутого пользователя из data и отрисовка пагинации без него
            await reload_reaction_pagination_after_hide_or_like(callback,
                                                                user_tg_id,
                                                                data,
                                                                keyboard,
                                                                list_type,
                                                                page)

            # вывожу уведомление
            await bot_notification_about_dislike(callback.message,
                                                 '❗️ <b>Пользователь удален из ваших контактов</b>\n'
                                                 'и добавлен в раздел:\n'
                                                 '"🚷 <b>Скрытые пользователи</b>"')

        # удаление пользователя из "Скрытые пользователи"
        elif callback_data.action == 'remove_from_ignore':

            # удаляем реакцию из бд (matchreactions)
            await asyncio.to_thread(remove_user_from_ignore_table, user_tg_id, current_user_id)

            # удаление пользователя из data и отрисовка пагинации без него
            await reload_reaction_pagination_after_hide_or_like(callback,
                                                                user_tg_id,
                                                                data,
                                                                keyboard,
                                                                list_type,
                                                                page)

            # вывожу уведомление
            await bot_notification_about_dislike(callback.message,
                                                 '☺️ <b>Пользователь снова доступен в поиске!</b>')

        # отрисовка клавиатуры при переключении между карточками
        else:

            await load_pagination_start_or_end_data(callback.message,
                                                    data,
                                                    keyboard,
                                                    list_type,
                                                    total_pages,
                                                    page=page)

    await callback.answer()


# Удаление лишних сообщений из чата (этот файл самая нижняя точка в иерархии)

'''
F.text – regular text message (this has already been done)
F.photo – message with photo
F.video – message with video
F.animation – message with animation (gifs)
F.contact – message sending contact details (very useful for FSM)
F.document – a message with a file (there may also be a photo if it is sent as a document)
F.data – message with CallData (this was processed in the previous article).
'''


@router.message(F.text | F.photo | F.video | F.animation |
                F.contact | F.document | F.sticker)
async def handle_random_message(message: Message):
    await message.delete()
    user_tg_id = message.from_user.id
    data = await asyncio.to_thread(check_user, user_tg_id)

    # если пользователь зарегистрирован
    if data:
        await attention_message(message, '⚠️ Если вы хотите внести изменения, перейдите '
                                'в раздел <b>"редактировать профиль"</b>', 3)
    else:
        await attention_message(message, '⚠️ Чтобы взаимодействовать с сервисом, '
                                'вам необходимо <b>зарегистрироваться</b>', 3)
