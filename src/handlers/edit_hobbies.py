import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.notifications import attention_message
from src.modules.delete_messages import del_last_message
from src.modules.get_self_data import get_user_info
from src.database.requests.hobbies_data import check_hobby, delete_hobby
from src.handlers.edit_name import check_emodji
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    hobby = State()
    hobby_del = State()


delete_messages = []
delete_last_message = []


# МЕНЮ РЕДАКТИРОВАНИЯ УВЛЕЧЕНИЙ

@router.callback_query(F.data == 'edit_hobbies')
async def edit_hobbies(callback: CallbackQuery, state: FSMContext):

    # очищаю состояние (на всякий случай)
    await state.clear()

    # получаю свой id
    user_tg_id = callback.from_user.id

    # отрисовка меню изменения увлечений
    await check_hobbies_list(user_tg_id, callback)


# ПРОВЕРКА НАЛИЧИЯ УВЛЕЧЕНИЙ (В ПРИНЦИПЕ) И ОТРИСОВКА МЕНЮ
# С КНОПКОЙ УДАЛЕНИЯ (ЕСЛИ ЕСТЬ) ИЛИ БЕЗ (ЕСЛИ УВЛЕЧЕНИЙ НЕТ)
# А ТАКЖЕ ПРОВЕРКА ПО КОЛИЧЕСТВУ УВЛЕЧЕНИЙ ДЛЯ ВЕРНОЙ ОТРИСОВКИ КЛАВИАТУРЫ

async def check_hobbies_list(user_tg_id, callback):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    hobbies_data = self_data[1]
    self_hobbies = user_info['hobbies']

    # если хобби нет (в таблице проставлен "-") отрисовка клавиатуры без укнопки удаления
    if self_hobbies == '-':
        try:

            # отрисовка страницы
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption='\n<b>Список ваших увлечений пуст 🤷‍♂️</b>',
                    parse_mode='HTML'
                ),
                reply_markup=kb.no_hobbies
            )
        except:

            try:
                await del_last_message(callback.message)
            except:
                pass

            await callback.message.answer_photo(
                photo=f'{self_data[0][1]}',
                caption='\n<b>Список ваших увлечений пуст 🤷‍♂️</b>',
                parse_mode='HTML',
                reply_markup=kb.no_hobbies
            )

    # если уже добавлено 5 увлечений (отрисовка с клавиатурой без кнопки добавить)
    elif len(hobbies_data) >= 7:

        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                        '\n\n⚠️ <b>Вы добавили максимальное количество увлечений.</b>'
                        '\nЧтобы добавить новое - удалите одно из имеющихся.'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.max_hobbies
            )

        except:

            try:
                await del_last_message(callback.message)
            except:
                pass

            await callback.message.answer_photo(
                photo=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                    '\n\n⚠️ <b>Вы добавили максимальное количество увлечений.</b>'
                    '\nЧтобы добавить новое - удалите одно из имеющихся.'
                ),
                parse_mode='HTML',
                reply_markup=kb.max_hobbies
            )

    # если хобби есть и не более 7 штук
    else:
        try:

            # отрисовка страницы
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{self_data[0][1]}',
                    caption=(
                        f'\n<b>Список ваших увлечений: </b>{self_hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.edit_hobbies
            )
        except:

            try:
                await del_last_message(callback.message)
            except:
                pass

            await callback.message.answer_photo(
                photo=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений: </b>{self_hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.edit_hobbies
            )


# МЕНЮ "ДОБАВЛЕНИЯ НОВОГО УВЛЕЧЕНИЯ"

@router.callback_query(F.data == 'new_hobby')
async def new_hobby(callback: CallbackQuery, state: FSMContext):

    # отрисовка меню добавления увлечения
    await new_hobby_menu(callback, state)

    # добавляю в состояние id собщения для редактирования
    await state.update_data(message_id=callback.message.message_id)


# ОТРИСОВКА МЕНЮ ДОБАВЛЕНИЯ УВЛЕЧЕНИЙ

async def new_hobby_menu(callback, state):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    self_hobbies = user_info['hobbies']

    try:

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                    '\n\n‼️ Добавьте <b>не более 7 увлечений</b>.'
                    '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                    '\n<b>Одно увлечение - одно сообщение</b>'
                    '\n(<u>не более 50 символов</u>)'
                    '\n\n💬 Отправьте увлечение сообщением в чат, '
                    'чтобы я мог его добавить:'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_hobbies
        )

    except:

        try:
            await del_last_message(callback.message)
        except:
            pass

        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ Добавьте <b>не более 5 увлечений</b>.'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить:'
            ),
            parse_mode='HTML',
            reply_markup=kb.back_hobbies
        )

    # устанавливаю состояние добавления нового увлечения
    await state.set_state(Registration.hobby)


# СОСТОЯНИЕ ОЖИДАНИЯ СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ С НАЗВАНИЕМ НОВОГО УВЛЕЧЕНИЯ

@router.message(Registration.hobby)
async def add_hobby(message: Message, state: FSMContext, bot: Bot):

    # удаляю сообщение пользователя из чата с новым увлечением
    await del_last_message(message)

    # получаю свой id
    user_tg_id = message.from_user.id

    # получаю id сообщения для редактирования из состояния
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # проверка длинны сообщения от пользователя и что оно является текстом
    if message.content_type == 'text' and len(message.text) <= 50:

        #  сохраняю текст сообщения и привожу к нижнему регистру
        hobby = message.text.lower()

        # проверяю на наличие эмодзи в сообщении
        emodji_checked = await check_emodji(hobby)

        # если в сообщении есть эмодзи
        if not emodji_checked:

            # вывожу уведомление об ошибке
            await wrong_hobby_name(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания сообщения с новым увлечением
            return

        # проверяю есть ли у пользователя уже такое увлечение
        checked = await asyncio.to_thread(check_hobby, user_tg_id, hobby)

        # если такое увлечение уже есть
        if not checked:

            # вывожу уведомление об ошибке
            await hobby_already_exist(user_tg_id, message_id, bot)

            # возвращаюсь в состояние ожидания сообщения с новым увлечением
            return

        # если все проверки прошли успешно
        else:

            # добавляю новое хобби в бд
            await hobby_succesful_added(user_tg_id, message_id, bot)

    # если сообщение не текстовое (фото, анимация и т.д.)
    else:

        # вывожу уведомление об ошибке
        await wrong_hobby_name(user_tg_id, message_id, bot)

        # возвращаюсь в состояние ожидания сообщения с новым увлечением
        return


# МЕНЮ УДАЛЕНИЯ УВЛЕЧЕНИЙ

@router.callback_query(F.data == 'del_hobby')
async def del_hobby(callback: CallbackQuery):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # отрисовка клавиатуры удаления увлечений если они есть у пользователя
    await check_hobby_to_delete(user_tg_id, callback)


# ОТРИСОВКА СТРАНИЦЫ С ИНЛАЙН КНОПКАМИ ДЛЯ УДАЛЕНИЯ КАЖДОГО УВЛЕЧЕНИЯ

async def check_hobby_to_delete(user_tg_id, callback):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    hobbies_data = self_data[1]
    self_hobbies = user_info['hobbies']

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.delete_hobbies_keyboard(user_tg_id, hobbies_data))

    except:

        try:
            await del_last_message(callback.message)
        except:
            pass

        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.delete_hobbies_keyboard(user_tg_id, hobbies_data))


# УДАЛЕНИЕ УВЛЕЧЕНИЯ

@router.callback_query(F.data.startswith('remove_hobby:'))
async def handle_remove_hobby(callback: CallbackQuery):
    user_tg_id = callback.from_user.id

    # полученный id преобразую в int
    hobby_id = int(callback.data.split(':')[1])

    # удаляю хобби из бд
    await asyncio.to_thread(delete_hobby, user_tg_id, hobby_id)

    # проверяю список хобби пользователя для верной отрисовки на странице
    # и отрисовываю клавиатуру удаления с учетом изменений
    await check_hobby_to_delete(user_tg_id, callback)

    # уведомление об успешном удалении
    await attention_message(callback.message, 'Увлечение удалено ✅', 1)


# УВЕДОМЛЕНИЕ ОБ ОШИБКЕ ЕСЛИ НЕВЕРНЫЙ ФОРМАТ ДАННЫХ

async def wrong_hobby_name(user_tg_id, message_id, bot):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    self_hobbies = user_info['hobbies']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
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
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n❌ Название увлечения должно содержать <b>только текст</b>'
                ', не должно содержать эмодзи и изображения, а так же '
                'не должно превышать длинну в <b>50 символов</b>.'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# ЕСЛИ ДОБАВЛЯЕМОЕ УВЛЕЧЕНИЕ УЖЕ ЕСТЬ В СПИСКЕ УВЛЕЧЕНИЙ У ПОЛЬЗОВАТЕЛЯ

async def hobby_already_exist(user_tg_id, message_id, bot):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    self_hobbies = user_info['hobbies']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n❌ Такое увлечение уже находится в вашем списке'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(2)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# УВЕДОМЛЕНИЕ И ОТРИСОВКА СТРАНИЦЫ ПОСЛЕ ДОБАВЛЕНИИ НОВОГО УВЛЕЧЕНИЯ

async def hobby_succesful_added(user_tg_id, message_id, bot):

    # плучаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    self_hobbies = user_info['hobbies']

    # отрисовка страницы
    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n✅ Увлечение успешно добавлено!'
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
                f'\n<b>Список ваших увлечений:</b>{self_hobbies}'
                '\n\n‼️ <u>Придерживайтесь принципа</u>:'
                '\n<b>Одно увлечение - одно сообщение</b>'
                '\n\n💬 Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )
