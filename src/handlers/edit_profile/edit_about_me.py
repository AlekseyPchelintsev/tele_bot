import asyncio
import re
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.modules.delete_messages import del_last_message
from src.database.requests.about_me_data import edit_about_me_data, delete_about_me_data
from src.modules.check_emoji import check_partial_markdown
from src.modules.moving_through_sections import check_menu_command
from config import exclude_text_message
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_about_me = State()


# МЕНЮ РЕДАКТИРОВАНИЯ О СЕБЕ
@router.callback_query(F.data == 'edit_about_me')
async def edit_about_me_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (на всякий случай)
    await state.clear()

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    about_me = user_info['about_me']

    # проверяю наличие записи в таблице aboutme
    if about_me == '-':

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '<b>Редактирование раздела</b>'
                    f'\n<b>О себе:</b> {about_me}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.edit_about_me_no_delete_button
        )

    else:

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    '<b>Редактирование раздела</b>'
                    f'\n<b>О себе:</b> {about_me}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.edit_about_me
        )


# ДОБАВЛЕНИЕ ДАННЫХ О СЕБЕ
@router.callback_query(F.data == 'add_about_me')
async def edit_about_me(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (на всякий случай)
    await state.clear()

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    about_me = user_info['about_me']

    # отрисовка страницы
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                '<b>Редактирование раздела</b>'
                f'\n<b>О себе:</b> {about_me}'
                '\n\n💬 <b>Пришлите в чат информацию для раздела "О себе".</b>'
                '\n\n📍 <u>Не используйте ненормативную лексику.</u>'
                '\n📍 <b>Относитесь уважительно к другим пользователям</b>!'
                '\n⚠️ (Длинна текста не должна превышать 200 символов):'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    # добавляю в состояние id сообщения для редактирования
    await state.update_data(message_id=edit_message.message_id)

    # устанавливаю состояние ожидания сообщения от пользователя с новым именем
    await state.set_state(Registration.change_about_me)


@router.message(Registration.change_about_me)
async def edit_about_me_state(message: Message, state: FSMContext, bot: Bot):

    # получаю свой id
    user_tg_id = message.from_user.id

    # получаю из состояния id сообщения для редактирования
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # получаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы при неверном формате
    self_data = user_info['data']
    about_me = user_info['about_me']

    # проверяю что сообщение текстовое
    if message.content_type == 'text':

        # сохраняю текст сообщения
        about_me_text = message.text

        if about_me_text not in exclude_text_message:

            # удаляю из чата присланное сообщение от пользователя с новым именем
            await del_last_message(message)

            # проверяю не содержит ли сообщение markdown разметку
            markdown_checked = await check_partial_markdown(about_me_text)

            # если содержит эмодзи
            if markdown_checked:

                # вывожу ошибку
                try:
                    await bot.edit_message_media(
                        chat_id=user_tg_id,
                        message_id=message_id,
                        media=InputMediaPhoto(
                            media=f'{self_data[0][1]}',
                            caption=(
                                '<b>Редактирование раздела</b>'
                                f'\n<b>О себе:</b> {about_me}'
                                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                                '\n\n❗️ Сведения "О себе" могут содержать '
                                '<b>только текст</b> (без специальных символов) <b>и эмодзи</b> 😉.'
                                '\n\n💬 <b>Пришлите в чат информацию для раздела "О себе".</b>'
                            ),
                            parse_mode='HTML'
                        ),
                        reply_markup=kb.back
                    )
                except Exception as e:
                    pass

                # возвращаюсь в состояние ожидания нового сообщения
                return

            # если сообщение больше 200 символов - обрезаю его и добавляю ... в конце
            if len(message.text) > 200:
                about_me_text = about_me_text[:200] + '...'

            # добавляю данные в бд
            await asyncio.to_thread(edit_about_me_data, user_tg_id, about_me_text)

            # получаю свои данные для отрисовки страницы с учетом изменений
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

            # отрисовка страницы
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
                        '\n\n✅ <i>Раздел "О себе" изменен</i>'
                        '\n\n<b>Редактировать:</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.about_me
            )

            # очищаю состояние
            await state.clear()

        # еслии текст содержит команду из клавиатуры
        else:

            # очищаю состояние, орабатываю ее и открываю
            # соответствующий пункт меню
            await check_menu_command(message, about_me_text, state)

    # если прислали не текст
    else:

        # удаляю из чата присланное сообщение от пользователя с новым именем
        await del_last_message(message)

        # отрисовка сообщения
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        '<b>Редактирование раздела</b>'
                        f'\n<b>О себе:</b> {about_me}'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Сведения "О себе" могут содержать '
                        '<b>только текст и эмодзи 😉</b>.'
                        '\n\n💬 <b>Пришлите в чат информацию для раздела "О себе".</b>'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.back
            )
        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания данных от пользователя
        return


@router.callback_query(F.data == 'delete_about_me')
async def delete_about_me(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # удалю запись из бд
    await asyncio.to_thread(delete_about_me_data, user_tg_id)

    # получаю свои данные для отрисовки страницы с учетом изменений
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

    # отрисовка страницы
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
                '\n\n✅ <i>Данные из раздела "О себе" удалены</i>'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )
