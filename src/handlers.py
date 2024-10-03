import asyncio
import logging
from time import sleep
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from src.modules.loader import loader, notification
from src.modules.delete_messages import del_messages, del_last_message
from src.database.models import async_session, User
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list
from src.database.requests.user_data import (get_data,
                                             get_user_data,
                                             check_user,)

from src.database.requests.photo_data import (update_user_photo,
                                              delete_user_photo,
                                              check_user_photo)

from src.database.requests.new_user import add_new_user, check_nickname

from src.database.requests.hobbies_data import check_hobby, delete_hobby
from src.database.requests.search_hobby import get_users_by_hobby
from config import no_photo_id
import src.keyboard as kb
# from src.database.models import get_db_connection

router = Router()


class Registration(StatesGroup):
    user_id = State()
    name = State()
    nickname = State()
    photo = State()
    gender = State()
    age = State()
    birth_date = State()
    message = State()
    callback = State()
    hobbie = State()
    search = State()
    hobby_del = State()


delete_messages = []
delete_last_message = []

# Входная точка


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    data = await asyncio.to_thread(check_user, user_tg_id)
    if data:
        await message.answer(
            text=(
                f'С возвращением, {data[1]}!\n'
                'Выберите раздел:'
            ), reply_markup=kb.main)
    else:
        await state.update_data(user_id=user_tg_id)
        await message.answer(text='Привет!\nЧтобы продолжить, вам нужно:',
                             reply_markup=kb.regkey)


@router.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await loader(callback.message, 'Загружаю')
    await del_last_message(callback.message)
    await state.set_state(Registration.name)
    await asyncio.sleep(.5)
    del_message = await callback.message.answer(text='Пожалуйста, ведите ваше имя:')
    delete_last_message.append(del_message.message_id)

# Получение данных пользователя и добавление их в бд


@router.message(Registration.name)
async def reg_name(message: Message, state: FSMContext, bot: Bot):
    # from main import bot
    await del_messages(message.chat.id, delete_last_message)
    delete_messages.append(message.message_id)

    user_tg_id = message.from_user.id
    name = message.text
    get_user_photo = await bot(GetUserProfilePhotos(user_id=user_tg_id))
    check_photo_id = get_user_photo.photos[0][-1].file_id
    get_user_nickname = message.from_user.username
    photo_id = await check_user_photo(check_photo_id)
    user_nickname = await check_nickname(get_user_nickname)

    await state.update_data(name=name, nickname=user_nickname, photo=photo_id)
    await loader(message, 'Обработка')
    # Пол
    await state.set_state(Registration.gender)
    await asyncio.sleep(.5)
    await message.answer(text='Укажите ваш пол.', reply_markup=kb.gender)

# Регистрация пола


@router.callback_query(Registration.gender, F.data.in_(['male', 'female', 'other']))
async def gender_checked(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    gender = callback.data
    await state.update_data(gender=gender)
    await loader(callback.message, 'Обработка')
    await asyncio.sleep(.5)
    await state.set_state(Registration.birth_date)
    del_message = await callback.message.answer(text='Укажите дату вашего рождения в формате "ДД.ММ.ГГГГ".')
    delete_messages.append(del_message.message_id)

# TODO Регистрация возраста


@router.message(Registration.birth_date)
async def age_checked(message: Message, state: FSMContext):
    chat_id = message.chat.id
    delete_messages.append(message.message_id)
    await loader(message, 'Обработка')
    date_input = message.text

    try:
        check_birth_date = datetime.strptime(date_input, '%d.%m.%Y')
        user_birth_date = check_birth_date.strftime('%d.%m.%Y')
        today_date = datetime.today()
        user_age = today_date.year - check_birth_date.year - (
            (today_date.month, today_date.day) <
            (check_birth_date.month, check_birth_date.day)
        )

    except ValueError:
        # Ввели не верный формат
        del_message = await message.answer(
            text='Пожалуйста, введите дату вашего рождения в формате "ДД.ММ.ГГГГ".'
        )
        delete_messages.append(del_message.message_id)
        await state.set_state(Registration.birth_date)
        return

    # Извлекаем данные из состояния
    data = await state.get_data()
    user_tg_id = data.get('user_id')
    name = data.get('name')
    photo_id = data.get('photo')
    nickname = data.get('nickname')
    gender = data.get('gender')

    # Функция добавления пользоваателя
    await asyncio.to_thread(
        add_new_user, user_tg_id, name, photo_id,
        nickname, gender, user_age, user_birth_date
    )

    await state.clear()
    await del_messages(chat_id, delete_messages)
    await notification(message, 'Вы успешно зарегистрированы!')
    await message.answer(
        text='Вы также можете рассказать о своих увлечениях людям, '
        'чтобы им было проще вас найти.',
        reply_markup=kb.start_edit
    )

# Главное меню


@router.callback_query(F.data == 'main_menu')
async def open_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await asyncio.sleep(.5)
    await callback.message.answer(text='Главное меню:', reply_markup=kb.users)

# Меню "помощь"


@router.callback_query(F.data == 'help')
async def open_help(callback: CallbackQuery):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await asyncio.sleep(.5)
    await callback.message.answer(text='Помощь:', reply_markup=kb.help_about)

# Вернуться назад


@router.callback_query(F.data == 'back')
async def back_to_main(callback: CallbackQuery):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await callback.message.answer(text='Выберите раздел:', reply_markup=kb.main)

# Меню "мой профиль"


@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await state.clear()
    await del_messages(callback.message.chat.id, delete_messages)
    user_id = callback.from_user.id
    # data = await get_user_data(user_id)
    data = await asyncio.to_thread(get_user_data, user_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    await asyncio.sleep(.5)
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Интересы:</b> {hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )
    except:
        try:
            await del_last_message(callback.message)
        except:
            pass
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Интересы:</b> {hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.about_me
        )

# Редактирование увлечений


@router.callback_query(F.data == 'edit_hobbies')
async def edit_hobbies(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Загружаю...')
    await del_messages(callback.message.chat.id, delete_messages)
    user_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_id)
    gender = await check_gender(data[0][3])
    hobbies = await hobbies_list(data[1])
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {data[0][0]}\n'
                    f'<b>Возраст:</b> {data[0][4]}\n'
                    f'<b>Пол:</b> {gender}\n'
                    f'<b>Интересы:</b> {hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.edit_hobbies)
    except:
        try:
            await del_last_message(callback.message)
        except:
            pass
        await callback.message.answer_photo(
            photo=f'{data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {data[0][0]}\n'
                f'<b>Возраст:</b> {data[0][4]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Интересы:</b> {hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.edit_hobbies
        )

# Меню "добавление хобби"


@router.callback_query(F.data == 'new_hobbie')
async def new_hobbie(callback: CallbackQuery, state: FSMContext):
    try:
        await del_last_message(callback.message)
    except:
        pass
    del_message = await callback.message.answer(
        text=(
            '<b>Расскажите о ваших увлечениях.</b>\n\n'
            '<i>Опишите их максимально коротко.</i>\n'
            '<i>Например:</i>\n\n'
            '⛔️<code>Плохое описание:</code> "Увлекаюсь ловлей рыбы на спиннинг"\n'
            '✅<b>Хорошее описание:</b> "рыбалка"\n\n'
            '⛔️<code>Плохое описание:</code> "С детства люблю шахматы. '
            'Являюсь фанатом Фишера и Каспарова"\n'
            '✅<b>Хорошее описание:</b> "шахматы"\n\n'
            '⛔️<code>Плохое описание:</code> "люблю смотреть аниме! '
            'Особенно "Ходячий замок" и "Унесенные призраками"\n'
            '✅<b>Хорошее описание:</b> "аниме"\n\n'
            '<b>Чем короче и содержательней будет описание, '
            'тем проще вас будет найти другим пользователям!</b>'
        ),
        parse_mode="HTML"
    )

    await asyncio.sleep(.2)
    del_message_second = await callback.message.answer(
        text=(
            '❗️<b>Придерживайтесь принципа:</b> '
            '"Одно увлечение - одно сообщение"'
        ),
        parse_mode="HTML"
    )

    await asyncio.sleep(.2)
    del_message_third = await callback.message.answer(
        text=(
            '⤵️ Отправьте ваше увлечение сообщением в чат, '
            'чтобы я мог его добавить.'
        ),
        reply_markup=kb.back_hobbies
    )

    delete_messages.clear()
    delete_last_message.clear()
    delete_messages.extend(
        [del_message.message_id, del_message_second.message_id])
    delete_last_message.append(del_message_third.message_id)
    await state.update_data(message=del_message_third)
    await state.set_state(Registration.hobbie)

# Добавление нового хобби


@router.message(Registration.hobbie)
async def add_hobbie(message: Message, state: FSMContext):
    await del_messages(message.chat.id, delete_last_message)
    await asyncio.sleep(.2)
    await loader(message, 'Обработка')
    hobbie = message.text.lower()
    user_id = message.from_user.id
    await state.update_data(hobbie=hobbie)
    checked = await asyncio.to_thread(check_hobby, user_id, hobbie)
    if not checked:
        await asyncio.sleep(.2)
        await notification(message, '❌ Такое увлечение уже находится в вашем списке')
        await asyncio.sleep(.2)
        response_message = await message.answer(
            text=(
                '⤵️ Отправьте ваше увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            reply_markup=kb.back_hobbies
        )
        delete_last_message.append(response_message.message_id)
    else:
        await asyncio.sleep(.2)
        await notification(message, '✅ Ваш список увлечений успешно обновлен!')
        await asyncio.sleep(.2)
        response_message_third = await message.answer(
            text=(
                '⤵️ Отправьте ваше увлечение сообщением в чат, '
                'чтобы я мог его добавить.'
            ),
            reply_markup=kb.back_hobbies
        )

        delete_last_message.append(response_message_third.message_id)
    await state.set_state(Registration.hobbie)

# Меню удаления хобби


@router.callback_query(F.data == 'del_hobbie')
async def del_hobby(callback: CallbackQuery, state: FSMContext):
    try:
        await del_last_message(callback.message)
    except:
        pass
    user_id = callback.from_user.id
    data = await asyncio.to_thread(get_user_data, user_id)
    hobbies = await hobbies_list(data[1])
    if hobbies != '-':
        response_message = await callback.message.answer(
            text=(
                f'<b>Список ваших увлечений:</b> \n\n{hobbies}\n\n'
                'Чтобы удалить увлечение, просто пришлите мне его в чат.'
            ),
            parse_mode='HTML',
            reply_markup=kb.back
        )

        await state.update_data(response_message_id=response_message.message_id)
        await state.set_state(Registration.hobby_del)
    else:
        response_message = await callback.message.answer(
            text=f'<b>Список ваших увлечений пуст.</b>',
            parse_mode='HTML',
            reply_markup=kb.add_hobby)
    delete_messages.append(response_message.message_id)

# Удаление хобби


@router.message(Registration.hobby_del)
async def del_hobby_from_db(message: Message, state: FSMContext):
    from main import bot
    user_id = message.from_user.id
    hobby = message.text
    hobby = hobby.lower()
    is_hobby = await asyncio.to_thread(delete_hobby, user_id, hobby)
    if is_hobby:
        await loader(message, 'Удаляю')
        await notification(message, 'Увлечение успешно удалено!')
        message_from_state = await state.get_data()
        response_message_id = message_from_state.get('response_message_id')
        data = await asyncio.to_thread(get_user_data, user_id)
        hobbies = await hobbies_list(data[1])
        if hobbies != '-':
            await message.bot.edit_message_text(
                chat_id=user_id,
                message_id=response_message_id,
                text=(
                    f'<b>Список ваших увлечений:</b> \n\n{hobbies}\n\n'
                    'Чтобы удалить увлечение, просто пришлите мне его в чат.'
                ),
                parse_mode='HTML',
                reply_markup=kb.back
            )

        else:
            await message.answer(
                text=f'<b>Список ваших увлечений пуст.</b>',
                parse_mode='HTML',
                reply_markup=kb.add_hobby
            )

            await message.bot.delete_message(chat_id=user_id,
                                             message_id=response_message_id)
    else:
        await notification(message, 'Такого хобби нет в вашем списке')

# Меню "редактировать фото"


@router.callback_query(F.data == 'edit_photo')
async def edit_photo_menu(callback: CallbackQuery):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await callback.message.answer(text='Выберите действие:',
                                  reply_markup=kb.edit_photo)

# Меню загрузки нового фото профиля


@router.callback_query(F.data == 'new_photo')
async def edit_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    sent_message = await callback.message.answer(
        text='Отправьте в чат фото, которое хотите загрузить.',
        reply_markup=kb.back_to_photo
    )
    await state.update_data(message=sent_message)
    await state.set_state(Registration.photo)

# Загрузка нового фото профиля


@router.message(Registration.photo)
async def get_new_photo(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    data = await state.get_data()  # данные предыдущего callback`a
    # данные последнего сообщения из предыдущего callback`a
    sent_message = data.get('message')
    await del_last_message(sent_message)
    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo=photo_id)
        await del_last_message(sent_message)
        await asyncio.to_thread(update_user_photo, user_tg_id, photo_id)
        await asyncio.sleep(.3)
        await loader(message, 'Фото загружается')
        await asyncio.sleep(.3)
        await message.answer(text='Фото профиля успешно обновлено ✅', reply_markup=kb.back)
        await state.clear()
    else:
        await del_last_message(sent_message)
        await loader(message, 'Обработка')
        await notification(message, '⚠️ Неизвестный формат файла ⚠️')
        response_message = await message.answer(
            text='Отправьте фото в формате <b>.jpg .jpeg</b> или <b>.png</b>',
            parse_mode='HTML',
            reply_markup=kb.back_to_photo
        )

        await state.update_data(message=response_message)

# Удаление фото профиля


@router.callback_query(F.data == 'del_photo')
async def delete_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await state.clear()
    user_tg_id = callback.from_user.id
    await asyncio.to_thread(delete_user_photo, user_tg_id)
    await state.clear()
    await loader(callback.message, 'Удаляю')
    await asyncio.sleep(.3)
    await callback.message.answer(text='Фото успешно удалено 🚫',
                                  reply_markup=kb.back)


# Меню "пользователи"

@router.callback_query(F.data == 'users')
async def check_users_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    await callback.message.answer(text='Выберите действие:',
                                  reply_markup=kb.users_menu)

# Меню поиска пользователей по хобби


@router.callback_query(F.data == 'search_users')
async def search_users_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Загружаю...')
    await del_last_message(callback.message)
    sent_message = await callback.message.answer(
        text='Пришлите в чат увлечение, по которому вы хотите найти пользователей:',
        reply_markup=kb.search_users
    )

    delete_messages.append(sent_message.message_id)
    await state.set_state(Registration.search)

# Поиск пользователей по хобби


@router.message(Registration.search)
async def search_users(message: Message, state: FSMContext):
    request = message.text
    request = request.lower()
    await state.update_data(search=request)
    data = await asyncio.to_thread(get_users_by_hobby, request)
    if not data:
        await loader(message, 'Обработка')
        await notification(message, '❌ Пользователи с таким увлечением отсутствуют')
        await asyncio.sleep(.5)
    else:
        await state.clear()
        await loader(message, 'Загружаю')
        try:
            await del_messages(message.chat.id, delete_messages)
        except:
            pass
        gender = await check_gender(data[0][4])
        hobbies = await hobbies_list(data[0][6])
        sleep(.5)
        await message.answer_photo(
            photo=f'{data[0][2]}',
            caption=(
                f'<b>Имя:</b> {data[0][1]}\n'
                f'<b>Возраст:</b> {data[0][5]}\n'
                f'<b>Пол:</b> {gender}\n'
                f'<b>Интересы:</b> {hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.paginator(list_type='hobbies_users')
        )

        await state.update_data(users_data=data)

# Отображение всех пользователей


@router.callback_query(F.data == 'all_users')
async def users_list(callback: CallbackQuery, state: FSMContext):
    # data = await get_data()
    # Параллельный запуск синхронной функции
    data = await asyncio.to_thread(get_data)
    gender = await check_gender(data[0][4])
    hobbies = await hobbies_list(data[0][6])
    await asyncio.sleep(.5)
    await del_last_message(callback.message)
    await callback.message.answer_photo(
        photo=f'{data[0][2]}',
        caption=(
            f'<b>Имя:</b> {data[0][1]}\n'
            f'<b>Возраст:</b> {data[0][5]}\n'
            f'<b>Пол:</b> {gender}\n'
            f'<b>Интересы:</b> {hobbies}'
        ),
        parse_mode='HTML',
        reply_markup=kb.paginator(list_type='all_users')
    )
    await state.update_data(users_data=data)


# Пагинация списка пользователей

@router.callback_query(
    kb.Pagination.filter(F.action.in_(
        ['prev', 'next', 'menu', 'user_profile']))
)
async def pagination_handler(
    callback: CallbackQuery,
    callback_data: kb.Pagination,
    state: FSMContext
):
    from main import bot
    list_type = callback_data.list_type
    data = (await state.get_data()).get('users_data')
    page_num = int(callback_data.page)
    chat_id = callback.message.chat.id
    if callback_data.action == 'prev':
        page = max(page_num - 1, 0)
    elif callback_data.action == 'next':
        page = min(page_num + 1, len(data) - 1)
    else:
        page = page_num

    if callback_data.action == 'menu':
        await del_last_message(callback.message)
        await bot.send_message(chat_id=chat_id,
                               text='Выберите раздел:',
                               reply_markup=kb.users)
    elif callback_data.action == 'user_profile':
        await open_profile(callback)
    else:
        with suppress(TelegramBadRequest):
            gender = await check_gender(data[page][4])
            hobbies = await hobbies_list(data[page][6])
            await callback.message.edit_media(  # Редактирование пагинации
                media=InputMediaPhoto(
                    media=f'{data[page][2]}',
                    caption=(
                        f'<b>Имя:</b> {data[page][1]}\n'
                        f'<b>Возраст:</b> {data[page][5]}\n'
                        f'<b>Пол:</b> {gender}\n'
                        f'<b>Интересы:</b> {hobbies}'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.paginator(page, list_type)
            )

    await callback.answer()

# TODO Просмотр карточки пользователя


@router.callback_query(F.data == 'user_profile')
async def open_profile(callback: CallbackQuery):
    await del_last_message(callback.message)
    await notification(callback.message, '🚧 Ведутся работы')
    await users_list(callback)

# devtools

# Вытягивает id фото
'''
@router.message(F.photo)
async def photo_nahui(message: Message):
  photo_data = message.photo[-1]
  await message.answer(f'id Этого изображения:\n{photo_data.file_id}')
'''
# Тест функций


@router.message(F.text == '/test')
async def test(message: Message):
    user_tg_id = message.from_user.id
    hobby = 'цц'
    test = await asyncio.to_thread(check_hobby, hobby)
    await message.answer(f'{test}')
