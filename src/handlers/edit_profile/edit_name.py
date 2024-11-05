import asyncio
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.database.requests.name_change import change_user_name
from src.modules.delete_messages import del_last_message
from src.modules.check_emoji import check_emoji, check_all_markdown
from config import exclude_text_message
from src.modules.moving_through_sections import check_menu_command
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    change_name = State()


# МЕНЮ РЕДАКТИРОВАНИЯ ИМЕНИ
@router.callback_query(F.data == 'edit_name')
async def edit_name_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние (на всякий случай)
    await state.clear()

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {self_data[0][0]}'
                '\n\n💬 <b>Пришлите в чат новое имя:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    # добавляю в состояние id сообщения для редактирования
    await state.update_data(message_id=edit_message.message_id)

    # устанавливаю состояние ожидания сообщения от пользователя с новым именем
    await state.set_state(Registration.change_name)


# СОСТОЯНИЕ ОЖИДАНИЯ СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ С НОВЫМ ИМЕНЕМ
@router.message(Registration.change_name)
async def edit_name(message: Message, state: FSMContext, bot: Bot):

    # получаю свой id
    user_tg_id = message.from_user.id

    # получаю из состояния id сообщения для редактирования
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # проверяю что сообщение текстовое и не более 20 символов
    if message.content_type == 'text' and len(message.text) < 25:

        # сохраняю текст сообщения
        user_name = message.text

        if user_name not in exclude_text_message:

            # удаляю из чата присланное сообщение от пользователя с новым именем
            await del_last_message(message)

            # привожу имя к заглавному
            user_name = message.text.title()

            # проверяю наличие эмодзи в сообщении
            emodji_checked = await check_emoji(user_name)
            markdown_checked = await check_all_markdown(user_name)

            # если эмодзи есть в сообщении
            if emodji_checked or markdown_checked:

                # вывожу уведомление об ошибке
                await wrong_name(user_tg_id, message_id, bot)

                # возвращаюсь в состояние ожидания нового сообщения с именем
                return

            # если все проверки прошли вношу изменение в бд и отрисовываю страницу
            await change_name(user_tg_id, message, user_name, message_id, bot)

            # очищаю состояние
            await state.clear()

        # если текст содержит команду из клавиатуры
        else:

            # очищаю состояние, орабатываю ее и открываю
            # соответствующий пункт меню
            await check_menu_command(user_tg_id, message, user_name, state)

    # если сообщение не текстовое (содержит фото, анимации и т.д.)
    else:

        # вывожу уведомление об ошибке
        await wrong_name(user_tg_id, message_id, bot)

        # возвращаюсь в состояние ожидания нового сообщения с именем
        return


# УВЕДОМЛЕНИЕ ЕСЛИ НЕВЕРНЫЙ ФОРМАТ ИМЕНИ
async def wrong_name(user_tg_id, message_id, bot):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    # отрисовка страницы с ошибкой
    try:
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Ваше текущее имя:</b> {self_data[0][0]}'
                    '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                    '\n\n❌ Имя должно содержать <b>только буквы</b>, не должно '
                    'содержать эмодзи и изображения, '
                    'а так же превышать длинну в <b>25 символов</b>.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back
        )
    except Exception as e:
        pass


# ВНЕСЕНИЕ ИЗМЕНЕНИЯ ИМЕНИ В БД И ОТРИСОВКА СТРАНИЦЫ
async def change_name(user_tg_id, message, user_name, message_id, bot):

    # внесение изменений в бд
    await asyncio.to_thread(change_user_name, user_tg_id, user_name)

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
                '\n\n✅ Имя успешно изменено'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )
