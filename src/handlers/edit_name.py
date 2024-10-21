import asyncio
import re
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.get_self_data import get_user_info
from src.database.requests.name_change import change_user_name
from src.modules.delete_messages import del_last_message
from src.modules.notifications import loader
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

    # удаляю из чата присланное сообщение от пользователя с новым именем
    await del_last_message(message)

    # получаю из состояния id сообщения для редактирования
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # проверяю что сообщение текстовое и не более 20 символов
    if message.content_type == 'text' and len(message.text) < 20:

        # сохраняю текст сообщения и привожу его к заглавному
        user_name = message.text.title()

        # проверяю наличие эмодзи в сообщении
        emodji_checked = await check_emodji(user_name)

        # если эмодзи есть в сообщении
        if not emodji_checked:

            # вывожу уведомление об ошибке
            await wrong_name(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания нового сообщения с именем
            return

        # если все проверки прошли вношу изменение в бд и отрисовываю страницу
        await change_name(user_tg_id, message, user_name, message_id, bot)

        # очищаю состояние
        await state.clear()

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

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {self_data[0][0]}'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {self_data[0][0]}'
                '\n\n❌ Имя должно содержать <b>только текст</b>, не должно '
                'содержать эмодзи и изображения, '
                'а так же не должно превышать длинну в <b>20 символов</b>.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# ВНЕСЕНИЕ ИЗМЕНЕНИЯ ИМЕНИ В БД И ОТРИСОВКА СТРАНИЦЫ
async def change_name(user_tg_id, message, user_name, message_id, bot):

    # плучаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваше текущее имя:</b> {self_data[0][0]}'
            ),
            parse_mode='HTML'
        )
    )

    await loader(message, 'Вношу изменения')

    # внесение изменений в бд
    await asyncio.to_thread(change_user_name, user_tg_id, user_name)

    # получаю свои данные для отрисовки страницы с учетом изменений
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы с учетом изменений
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Ваше имя:</b> {self_data[0][0]}'
                '\n\nИмя успешно изменено ✅'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'<b>Имя:</b> {self_data[0][0]}'
                f'\n<b>Возраст:</b> {self_data[0][4]}'
                f'\n<b>Пол:</b> {self_gender}'
                f'\n<b>Город:</b> {self_data[0][5]}'
                f'\n\n<b>Увлечения:</b> {self_hobbies}'
                f'\n\n<b>О себе:</b> {about_me}'
                '\n\n<b>Редактировать:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.about_me
    )


# ЛОГИКА ПРОВЕРКИ НА НАЛИЧИЕ ЭМОДЗИ В СООБЩЕНИИ (ПЕРЕНЕСТИ)
async def check_emodji(user_name):
    check = re.search(r'('
                      r'[\U0001F600-\U0001F64F]|'
                      r'[\U0001F300-\U0001F5FF]|'
                      r'[\U0001F680-\U0001F6FF]|'
                      r'[\U0001F700-\U0001F77F]|'
                      r'[\U0001F800-\U0001F8FF]|'
                      r'[\U0001F900-\U0001F9FF]|'
                      r'[\U0001FA00-\U0001FAFF]|'
                      r'[\U00002700-\U000027BF]'
                      r')', user_name)
    return check is None
