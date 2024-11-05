import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from src.modules.get_self_data import get_user_info
from aiogram.fsm.context import FSMContext
from src.database.requests.employment_change import change_user_employment
from src.modules.check_emoji import check_emoji, check_all_markdown, check_partial_markdown
from src.modules.moving_through_sections import check_menu_command
from config import exclude_text_message

import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    edit_employment = State()


@router.callback_query(F.data == 'edit_employment')
async def change_employment(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                '\n<b>Выберите один из вариантов:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.edit_job_or_study
    )


@router.callback_query(F.data.in_(['work', 'study', 'search_myself']))
async def employment_changed(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    if callback.data == 'work':

        employment = 'Работаю'

        # отрисовка страницы
        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '\n✏️ Напишите коротко <b>кем и в какой сфере вы работаете</b>:'),
                parse_mode='HTML'
            ),
            reply_markup=kb.back
        )

        await state.update_data(employment=employment,
                                message_to_edit=message_to_edit.message_id)
        await state.set_state(Registration.edit_employment)

    elif callback.data == 'study':

        employment = 'Учусь'

        # отрисовка страницы
        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '\n✏️ Напишите <b>где и на кого вы учитесь</b>:'),
                parse_mode='HTML'
            ),
            reply_markup=kb.back
        )

        await state.update_data(employment=employment,
                                message_to_edit=message_to_edit.message_id)
        await state.set_state(Registration.edit_employment)

    elif callback.data == 'search_myself':

        employment = 'В поиске себя'
        employment_info = '👀'

        # изменение данных в бд
        await asyncio.to_thread(change_user_employment,
                                user_tg_id,
                                employment,
                                employment_info)

        # плучаю свои данные
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы с учетом изменений
        self_data = user_info['data']
        self_photo = self_data[0][1]
        self_name = self_data[0][0]
        self_age = self_data[0][4]
        self_city = self_data[0][5]
        self_gender = user_info['gender']
        self_hobbies = user_info['hobbies']
        about_me = user_info['about_me']
        # учеба/работа
        employment = user_info['employment']
        employment_info = user_info['employment_info']

        # отрисовка страницы с учетом внесенных изменений
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_photo}',
                caption=(
                    f'{self_gender}'  # пол
                    f' • {self_name}'  # имя
                    f' • {self_age}'  # возраст
                    f' • {self_city}'  # город
                    f'\n► <b>{employment}:</b> {employment_info}'
                    f'\n► <b>Увлечения:</b> {self_hobbies}'
                    f'\n► <b>О себе:</b> {about_me}'
                    '\n\nДанные успешно изменены ✅'
                    '\n\n<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )

        # ДОПИСАТЬ


@router.message(Registration.edit_employment)
async def changed_employment(message: Message, state: FSMContext, bot: Bot):

    # получаю свой id
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    data_state = await state.get_data()
    message_id = data_state.get('message_to_edit')
    employment = data_state.get('employment')

    # завожу проверку на текст и отсутствие смайлов в сообщении
    if message.content_type == 'text':

        # сохраняю текст сообщения и привожу его к заглавному
        employment_info = message.text

        # поверка на наличие команды с клавиатуры
        if employment_info not in exclude_text_message:

            # удаляю сообщение от пользователя
            await message.delete()

            # если сообщение больше 100 символов - обрезаю его и добавляю ... в конце
            if len(message.text) > 100:
                employment_info = employment_info[:100] + '...'

            # проверяю наличие эмодзи и markdown разметки в сообщении
            emodji_checked = await check_emoji(employment_info)
            markdown_checked = await check_partial_markdown(employment_info)

            # если эмодзи есть в сообщении
            if emodji_checked or markdown_checked:

                # плучаю свои данные
                user_info = await get_user_info(user_tg_id)

                # Извлекаю свои данные для отрисовки страницы с учетом изменений
                self_data = user_info['data']
                self_photo = self_data[0][1]

                # вывожу уведомление об ошибке
                try:
                    await bot.edit_message_media(
                        chat_id=user_tg_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=self_photo,
                            caption=(
                                '⚠️ <b>Неверный формат данных</b> ⚠️'
                                '\n\n❗️ Описание должно содержать '
                                '<b>только текст</b>, не должно содержать эмодзи, '
                                'а также превышать длинну в <b>100 символов</b>.'
                                '\n\nОтправьте описание в чат еще раз:'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.back
                    )
                except Exception as e:
                    pass

                # возвращаюсь в состояние ожидания нового сообщения с именем
                return

            # изменение данных в бд
            await asyncio.to_thread(change_user_employment,
                                    user_tg_id,
                                    employment,
                                    employment_info)

            # плучаю свои данные
            user_info = await get_user_info(user_tg_id)

            # Извлекаю свои данные для отрисовки страницы с учетом изменений
            self_data = user_info['data']
            self_photo = self_data[0][1]
            self_name = self_data[0][0]
            self_age = self_data[0][4]
            self_city = self_data[0][5]
            self_gender = user_info['gender']
            self_hobbies = user_info['hobbies']
            about_me = user_info['about_me']
            # учеба/работа
            employment = user_info['employment']
            employment_info = user_info['employment_info']

            # отрисовка страницы с учетом внесенных изменений
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{self_photo}',
                    caption=(
                        f'{self_gender}'  # пол
                        f' • {self_name}'  # имя
                        f' • {self_age}'  # возраст
                        f' • {self_city}'  # город
                        f'\n► <b>{employment}:</b> {employment_info}'
                        f'\n► <b>Увлечения:</b> {self_hobbies}'
                        f'\n► <b>О себе:</b> {about_me}'
                        '\n\nДанные успешно изменены ✅'
                        '\n\n<b>Редактировать:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.about_me
            )

            await state.clear()

        # еслии текст содержит команду из клавиатуры
        else:

            # очищаю состояние, орабатываю ее и открываю
            # соответствующий пункт меню
            await check_menu_command(message, employment_info, state)

    else:

        # удаляю сообщение от пользователя
        await message.delete()

        # плучаю свои данные
        user_info = await get_user_info(user_tg_id)

        # Извлекаю свои данные для отрисовки страницы с учетом изменений
        self_data = user_info['data']
        self_photo = self_data[0][1]

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=self_photo,
                    caption=(
                        '⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Описание не должно содержать изображения или '
                        'любой отличный от текста контент, '
                        'а также превышать длинну в <b>100 символов</b>.'
                        '\n\nОтправьте описание в чат еще раз:'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.back
            )

        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания нового сообщения с именем
        return
