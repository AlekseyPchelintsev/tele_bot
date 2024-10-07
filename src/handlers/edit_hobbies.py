import asyncio
import logging
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.loader import loader
from src.modules.delete_messages import del_last_message
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import get_user_data
from src.database.requests.hobbies_data import check_hobby, delete_hobby
from src.modules.check_gender import check_gender
from src.handlers.edit_name import check_emodji
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    hobby = State()
    hobby_del = State()


delete_messages = []
delete_last_message = []


# Редактирование увлечений


@router.callback_query(F.data == 'edit_hobbies')
async def edit_hobbies(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    user_tg_id = callback.from_user.id
    await check_hobbies_list(user_tg_id, callback)

# Меню "добавление хобби"


@router.callback_query(F.data == 'new_hobby')
async def new_hobby(callback: CallbackQuery, state: FSMContext):
    await new_hobby_menu(callback, state)
    await state.update_data(message_id=callback.message.message_id)
    await state.set_state(Registration.hobby)

# Добавление нового хобби


@router.message(Registration.hobby)
async def add_hobby(message: Message, state: FSMContext, bot: Bot):
    await del_last_message(message)

    user_tg_id = message.from_user.id
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    if message.content_type == 'text' and len(message.text) <= 20:
        hobby = message.text.lower()
        emodji_checked = await check_emodji(hobby)

        if not emodji_checked:
            await wrong_hobby_name(user_tg_id, message_id, bot)
            return

        checked = await asyncio.to_thread(check_hobby, user_tg_id, hobby)

        if not checked:
            await hobby_already_exist(user_tg_id, message_id, bot)
            return

        else:
            await hobby_succesful_added(user_tg_id, message_id, bot)

    else:
        await wrong_hobby_name(user_tg_id, message_id, bot)
        return

# Меню удаления хобби


@router.callback_query(F.data == 'del_hobby')
async def del_hobby(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    await check_hobby_to_delete(user_tg_id, callback)

# Удаление хобби


@router.callback_query(F.data.startswith('remove_hobby:'))
async def handle_remove_hobby(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    hobby_name = callback.data.split(':')[1]
    await asyncio.to_thread(delete_hobby, user_tg_id, hobby_name)
    await check_hobby_to_delete(user_tg_id, callback)


# Логика удаления хобби

async def check_hobbies_list(user_tg_id, callback):

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    if hobbies == '-':
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'<b>Список ваших увлечений:</b>\n{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.no_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'<b>Список ваших увлечений:</b>\n{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.no_hobbies)
    else:
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'<b>Список ваших увлечений:</b>\n{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.edit_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'<b>Список ваших увлечений:</b>\n{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.edit_hobbies)


async def check_hobby_to_delete(user_tg_id, callback):

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies_data = data[1]
    hobbies = await hobbies_list(data[1])

    if hobbies == '-':

        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'<b>Список ваших увлечений:</b>\n{hobbies}'
                        'Список ваших увлечений пуст 🤷‍♂️'
                    ),
                    parse_mode='HTML'
                )
            )

            await loader(callback.message, 'Загружаю')

            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'<b>Список ваших увлечений:</b>\n{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.no_hobbies)
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'<b>Список ваших увлечений:</b>\n{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.no_hobbies)
    else:

        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=f'{data[0][1]}',
                    caption=(
                        f'<b>Список ваших увлечений:</b>\n{hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.delete_hobbies_keyboard(hobbies_data))
        except:
            await callback.message.answer_photo(
                photo=f'{data[0][1]}',
                caption=(
                    f'<b>Список ваших увлечений:</b>\n{hobbies}'
                ),
                parse_mode='HTML',
                reply_markup=kb.delete_hobbies_keyboard(hobbies_data))


# Меню добавления хобби

async def new_hobby_menu(callback, state):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    '⛔️ Плохой пример: ираю на гитаре\n'
                    '✅ Хороший пример: гитара\n\n'
                    '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                    '✅ Хороший пример: столяр\n\n'
                    '⛔️ Плохой пример: бухгалтерские услуги\n'
                    '✅ Хороший пример: бухгалтерия\n\n'
                    'Придерживайтесь принципа:'
                    '   <b>Одно увлечение - одно сообщение</b>\n\n'
                    f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                    '⤵️ Отправьте увлечение сообщением в чат, '
                    'чтобы я мог его добавить.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.back_hobbies
        )
    except:
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '⤵️ Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML',
            reply_markup=kb.back_hobbies
        )

    await state.set_state(Registration.hobby)


# Неверный формат данных

async def wrong_hobby_name(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '⚠️ Неверный формат данных ⚠️'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '❌ Название увлечения должно содержать только текст, не должно содержать эмодзи '
                'и изображения, а так же не должно превышать длинну в <b>20 символов</b>.\n\n'
                '⤵️ Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


async def hobby_already_exist(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '❌ Такое увлечение уже находится в вашем списке'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(2)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '⤵️ Отправьте <b>новое</b> увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )


# Логика добавления хобби

async def hobby_succesful_added(user_tg_id, message_id, bot):

    data = await asyncio.to_thread(get_user_data, user_tg_id)
    hobbies = await hobbies_list(data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '✅ Список ваших увлечений успешно обновлен!'
            ),
            parse_mode='HTML'
        )
    )

    await asyncio.sleep(1.5)

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{data[0][1]}',
            caption=(
                '⛔️ Плохой пример: ираю на гитаре\n'
                '✅ Хороший пример: гитара\n\n'
                '⛔️ Плохой пример: увлекаюсь деревообработкой\n'
                '✅ Хороший пример: столяр\n\n'
                '⛔️ Плохой пример: бухгалтерские услуги\n'
                '✅ Хороший пример: бухгалтерия\n\n'
                'Придерживайтесь принципа:'
                '   <b>Одно увлечение - одно сообщение</b>\n\n'
                f'<b>Список ваших увлечений:</b>\n{hobbies}\n\n\n'
                '⤵️ Отправьте увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.back
    )

# Неверный формат данных при поиске пользователей по хобби


async def wrong_search_hobby_name(user_tg_id, message_id, bot):

    self_data = await asyncio.to_thread(get_user_data, user_tg_id)
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

    await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                '⚠️ Неверный формат данных ⚠️'
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
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}\n\n'
                '❌ Название увлечения должно содержать только текст, не должно содержать эмодзи '
                'или изображения.\n\n'
                '<b>Пришлите в чат увлечение, по которому вы хотите найти пользователей:</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.search_users
    )
