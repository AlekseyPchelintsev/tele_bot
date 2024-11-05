import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import city_search, hobby_search, exclude_text_message
from src.modules.moving_through_sections import check_menu_command
from src.modules.pagination_logic import no_data_after_reboot_bot_reactions
from src.handlers.search_users.hobby_search import search_users_by_hobby
from src.modules.delete_messages import del_last_message
from src.modules.get_self_data import get_user_info
from src.modules.check_emoji_and_markdown import check_emoji, check_all_markdown
from src.database.requests.search_users import (check_users_in_city)
from src.handlers.search_users.error_handlers_search import wrong_search_city_name

import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    search_city = State()
    search_hobby = State()


delete_messages = []
delete_last_message = []


# ================================
# ПОИСК ЛЮДЕЙ ПО ГОРОДАМ         |
# ================================


async def serach_users_by_city(callback, state):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)
    city_data = user_info['data'][0][5]

    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{city_search}',
            caption=(
                '\n🔎 <b>В каком городе?</b>'
                '\n\n📌💬 Пришлите <b>название города</b> в чат'
                '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_in_city(city_data)
    )

    await state.update_data(message_id=edit_message.message_id)
    await state.set_state(Registration.search_city)


# поиск в моем городе или в любом


@router.callback_query(F.data.in_(['home_city', 'all_cities']))
async def search_in_city(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    search_data = callback.data

    # получаю данные пола из состояния
    search_gender = await state.get_data()
    gender_data = search_gender.get('type_of_gender')

    # поверяю наличие gender_data в состоянии
    if not gender_data:

        # уведомление об ошибке если данных в состоянии нет
        # (непредвиденные происшествия с сервером)
        await no_data_after_reboot_bot_reactions(callback.message, 'search_users')

    else:

        if search_data == 'home_city':

            # плучаю свои данные
            user_info = await get_user_info(user_tg_id)

            # Извлекаю название своего города
            city_data = user_info['data'][0][5]

            print(f'ВЫБРАН ПОИСК В МОЕМ ГОРОДЕ')
            print(f'ДАННЫЕ ГОРОДА: {city_data}, ПОЛА:{gender_data}')

            # проверяю наличие пользователей по запрошенному полу в своем городе
            check_home_city_users = await asyncio.to_thread(check_users_in_city,
                                                            user_tg_id,
                                                            city_data,
                                                            gender_data)

            if check_home_city_users:

                print(f'ПОЛЬЗОВАТЕЛИ В МОЕМ ГОРОДЕ ПО ПОЛУ НАЙДЕНЫ')

                # добавляю в состояние название своего города
                await state.update_data(city_users=city_data)
                await search_users_by_hobby(callback, state)

            else:

                print(f'ПОЛЬЗОВАТЕЛИ В МОЕМ ГОРОДЕ ПО ПОЛУ НЕ НАЙДЕНЫ')

                try:
                    await callback.message.edit_media(
                        media=InputMediaPhoto(
                            media=f'{city_search}',
                            caption=(
                                '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                                '\n\n📌⌨️ Вы можете выбрать пункт <b>"Не важно"</b> '
                                'чтобы посмотреть пользователей во всех городах'
                                '\n\n📌💬 или <b>пришлите в чат</b> название города, '
                                'чтобы найти в нем пользователей:'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.search_in_city(city_data)
                    )
                except:
                    await callback.message.answer_photo(
                        photo=f'{city_search}',
                        caption=(
                            '\n<b>Пользователи в вашем городе не найдены</b> 😔'
                            '\n\n📌⌨️ Вы можете выбрать пункт <b>"Не важно"</b> '
                            'чтобы посмотреть пользователей во всех городах'
                            '\n\n📌💬 или <b>пришлите в чат</b> название города, '
                            'чтобы найти в нем пользователей:'
                        ),
                        parse_mode='HTML',
                        reply_markup=kb.search_in_city(city_data)
                    )
                await state.set_state(Registration.search_city)

        elif search_data == 'all_cities':

            print('ВЫБРАН ПОИСК ПО ВСЕМ ГОРОДАМ')

            await state.update_data(city_users='all')
            await search_users_by_hobby(callback, state)


# поиск по конкретному городу


@router.message(Registration.search_city)
async def search_by_city(message: Message, state: FSMContext, bot: Bot):

    print(f'НАЗВАНИЕ ГОРОДА ОТПРАВЛЕНО В ЧАТ')

    user_tg_id = message.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)
    # Извлекаю название своего города
    city_data = user_info['data'][0][5]

    # удаляю сообщение отправленное в чат
    await del_last_message(message)

    # получаю данные пола из состояния
    search_gender = await state.get_data()
    gender_data = search_gender.get('type_of_gender')

    # поверяю наличие gender_data в состоянии
    if not gender_data:

        # уведомление об ошибке если данных в состоянии нет
        # (непредвиденные происшествия с сервером)
        await no_data_after_reboot_bot_reactions(message, 'search_users')

    else:

        # получаю id сообщения для редактирования
        edit_message = await state.get_data()
        message_id = edit_message.get('message_id')

        # проверка что сообщение текстовое, а не медиа (картинки, стикеры и т.д.)
        if message.content_type == 'text':

            # получаю текст сообщения для проверки на команды реплай клавиатуры
            city_name = message.text

            # проверяю наличие команд из клавиатуры
            if city_name not in exclude_text_message:

                # если сообщение не содержит команд - продолжаю его обработку
                city_name = message.text.title()

                # проверка на наличие смайлов в сообщении
                emodji_checked = await check_emoji(city_name)
                markdown_checked = await check_all_markdown(city_name)

                if emodji_checked or markdown_checked:
                    await wrong_search_city_name(user_tg_id, message_id, bot)
                    return

                # проверяю наличие хотя бы одного пользователя по уловиям
                check_users_city = await asyncio.to_thread(check_users_in_city,
                                                           user_tg_id,
                                                           city_name,
                                                           gender_data)

                if check_users_city:

                    await bot.edit_message_media(
                        chat_id=user_tg_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=f'{hobby_search}',
                            caption=(
                                '\n🔎 <b>Какие увлечения?</b>'
                                '\n\n📌💬 Пришлите <b>увлечение</b> в чат'
                                '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.hobbies_search
                    )

                    await state.update_data(city_users=city_name)
                    await state.set_state(Registration.search_hobby)

                else:

                    await bot.edit_message_media(
                        chat_id=user_tg_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=f'{city_search}',
                            caption=(
                                '\n🔎 <b>В каком городе?</b>'
                                f'\n\n❌ Пользователи в городе <b>"{
                                    city_name}"</b> '
                                '<u>не найдены.</u>'
                                '\n\n📌💬 Попробуйте поискать в <b>других городах</b>'
                                '\n\n📌⌨️ или <b>выберите один из вариантов</b> ниже'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.search_in_city(city_data)
                    )

            # если была прислана команда из клавиатуры
            else:

                # обрабатываю ее очищая состояние и перехожу
                # в пункт меню согласно команде
                await check_menu_command(user_tg_id, message, city_name, state)

        # если в сообщениии получен медиа контент вместо текста
        else:
            await wrong_search_city_name(user_tg_id, message_id, bot)
            return
