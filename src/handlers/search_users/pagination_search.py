import asyncio
from aiogram.types import CallbackQuery
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.handlers.reactions_menu.notice_reaction import bot_notification_about_like, bot_notification_about_dislike, bot_send_message_about_like, bot_send_message_matchs_likes
from src.modules.pagination_logic import (no_data_after_reboot_bot_reactions,
                                          back_callback,
                                          load_pagination_start_or_end_data)

from src.database.requests.likes_users import (insert_reaction,
                                               delete_and_insert_reactions,
                                               check_matches_two_users,
                                               send_user_to_ignore_table)

from src.modules.notifications import attention_message
import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# повторяющаяся логика отрисовки пагинации при отправке реакции/удалении анкеты из поиска
async def reload_pagination_after_hide_or_like(callback,
                                               user_tg_id,
                                               data,
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
                            'search_users',
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
                                                'paginator',
                                                list_type,
                                                total_pages,
                                                page=page)


# пагинация поиска пользователей
@ router.callback_query(
    kb.Pagination.filter(F.action.in_(
        ['prev',
         'next',
         'menu',
         'like',
         'hide']
    ))
)
async def pagination_handler(
    callback: CallbackQuery,
    callback_data: kb.Pagination,
    state: FSMContext,
    bot: Bot
):
    user_tg_id = callback.message.chat.id
    list_type = callback_data.list_type

    data = (await state.get_data()).get('users_data')

    # если бот ушел в ребут с открытой пагинацией у пользователя и данных нет
    if not data:
        await no_data_after_reboot_bot_reactions(callback, 'search_users')

    # Загрузка пагинации если data не None
    else:

        # общая длинна data для правильной отрисовки клавиатуры
        total_pages = len(data)

        page_num = int(callback_data.page)

        if callback_data.action == 'prev':
            page = max(page_num - 1, 0)
        elif callback_data.action == 'next':
            page = min(page_num + 1, len(data) - 1)
        else:
            page = page_num

        # нажатие на кнопку "Назад"
        if callback_data.action == 'menu':

            # Выход из пагинации (четвертый параметр - текст под инфой пользователя (не обязательный))
            menu_text = '🔎 <b>Выберите один из вариантов поиска:</b>'
            await back_callback(callback.message,
                                user_tg_id,
                                'users_menu',
                                'search',
                                menu_text)

        # обработка кнопок "отправить реакцию" и "скрыть пользователя"
        elif callback_data.action in ['hide', 'like']:

            # id текущего пользователя (просматриваемого)
            current_user_id = data[page][0]

            # лайк карточки пользователя
            if callback_data.action == 'like':

                # добавление записи в бд
                await asyncio.to_thread(insert_reaction,
                                        user_tg_id,
                                        current_user_id)

                # поверка наличи ответных записей в userreactions
                check = await asyncio.to_thread(check_matches_two_users,
                                                user_tg_id,
                                                current_user_id)

                # если запись есть
                if check:

                    # удаляем записи из userreactions и переносим в matchreactions
                    await asyncio.to_thread(delete_and_insert_reactions,
                                            user_tg_id,
                                            current_user_id)

                    # функция отправки сообщения обоим пользователям
                    await bot_send_message_matchs_likes(user_tg_id,
                                                        current_user_id,
                                                        bot)

                    # удаление текущего пользователя из data и отрисовка пагинации
                    await reload_pagination_after_hide_or_like(callback,
                                                               user_tg_id,
                                                               data,
                                                               list_type,
                                                               page)

                # если нет входящей реакции от пользователя
                if not check:

                    # отправляем уведомление пользователю
                    await bot_send_message_about_like(user_tg_id,
                                                      current_user_id,
                                                      bot)

                    # удаление текущего пользователя из data и отрисовка пагинации без него
                    await reload_pagination_after_hide_or_like(callback,
                                                               user_tg_id,
                                                               data,
                                                               list_type,
                                                               page)

                    # всплывающее уведомление для "меня"
                    await bot_notification_about_like(callback.message)

            # добавить пользователя в "скрытые пользователи" и убрать из поиска
            if callback_data.action == 'hide':

                # добавляю в список "скрытые пользователи"
                await asyncio.to_thread(send_user_to_ignore_table,
                                        user_tg_id,
                                        current_user_id)

                # удаление текущего пользователя из data и отрисовка пагинации
                await reload_pagination_after_hide_or_like(callback,
                                                           user_tg_id,
                                                           data,
                                                           list_type,
                                                           page)

                # уведомление "мне"
                text_info_hide_user = '🚷 Анкета добавлена в раздел <b>"Скрытые пользователи"</b> и удалена из поиска.'
                await bot_notification_about_dislike(callback.message,
                                                     text_info_hide_user)

        # обработка перелистывания анкет
        else:

            # отрисовывает клавиатуру даже если пользователи кончились
            await load_pagination_start_or_end_data(callback.message,
                                                    data,
                                                    'paginator',
                                                    list_type,
                                                    total_pages,
                                                    page=page)

    await callback.answer()
