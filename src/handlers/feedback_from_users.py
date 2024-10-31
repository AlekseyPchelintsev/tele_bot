import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from config import main_menu_logo, feedback_chat_id, feedback_menu_logo
from src.modules.notifications import notification
from src.modules.delete_messages import del_last_message
import src.modules.keyboard as kb


router = Router()


class Registration(StatesGroup):
    feedback = State()


# меню обратной связи
@router.callback_query(F.data == 'feedback')
async def feedback_from_users(callback: CallbackQuery, state: FSMContext):

    # отрисовываю страницу
    try:
        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=feedback_menu_logo,
                caption=(
                    '<i>Здесь вы можете написать разработчикам свои отзывы и '
                    'пожелания, а также сообщить о возникновении трудностей '
                    'в процессе взаиимодействия с сервисом.</i>'
                    '\n\n<b>Напишите ваше обращение в чат:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_to_main_menu
        )
    except:
        message_to_edit = await callback.message.send_photo(
            photo=feedback_menu_logo,
            caption=(
                '<i>Здесь вы можете написать разработчикам свои отзывы и '
                'пожелания, а также сообщить о возникновении трудностей '
                'в процессе взаиимодействия с сервисом.</i>'
                '\n\n<b>Напишите ваше обращение в чат:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.back_to_main_menu
        )

    # сохраняю в состоянии сообщение для редактирования и перехожу в состояние
    # ожидания сообщения от пользователя
    await state.update_data(message_to_edit=message_to_edit.message_id)
    await state.set_state(Registration.feedback)


# обработчик сообщения от пользователя
@router.message(Registration.feedback)
async def get_user_feedback(message: Message, state: FSMContext, bot: Bot):

    # получаю id пльзователя
    user_tg_id = message.from_user.id

    # сохраняю текст сообщения пользователя
    feedback_from_user = message.text

    # удаляю сообщение пользователя из чата
    await del_last_message(message)

    # получаю данные пользователя для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю данные пользователя для отрисовки страницы
    user_data = user_info['data']
    gender = user_info['gender']
    photo = user_data[0][1]
    name = user_data[0][0]
    age = user_data[0][4]
    city = user_data[0][5]

    # получаю данные для редактирования сообщения
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # отрисовка страницы пользователя после отправки обращения
    try:
        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=main_menu_logo,
                caption='<b>Главное меню:</b>',
                parse_mode='HTML'
            ),
            reply_markup=kb.users
        )
    except:
        await bot.send_photo(
            chat_id=user_tg_id,
            photo=main_menu_logo,
            caption='<b>Главное меню:</b>',
            parse_mode='HTML',
            reply_markup=kb.users
        )

    # оптравляю сообщение в чат админам
    await bot.send_photo(
        chat_id=feedback_chat_id,
        photo=photo,
        caption=(
            '<b>Сообщение от пользователя:</b>'
            f'\n\n<b>id пльзователя:</b> {user_tg_id}'
            f'\n{gender}'  # пол
            f' • {name}'  # имя
            f' • {age}'  # возраст
            f' • {city}'  # город
            f'\n\n{feedback_from_user}'),
        parse_mode='HTML'
    )

    # очищаю состояние
    await state.clear()

    # вывожу всплывающее уведомление пользователю
    await notification(message, '✅ Ваше обращение отправлено разработчикам.')
