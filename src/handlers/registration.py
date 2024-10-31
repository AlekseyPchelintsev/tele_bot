import asyncio
from datetime import datetime
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.notifications import notification
from config import video_no_nickname, in_progress, no_photo_id, main_menu_logo, registration_menu
from src.modules.delete_messages import del_last_message
from src.database.requests.new_user import add_new_user
from src.database.requests.user_data import check_user
from src.database.requests.birth_date_errors_on_reg import birth_date_error_catcher
from src.modules.check_emoji import check_emoji, check_all_markdown, check_partial_markdown
from src.handlers.for_admin.check_users_photos import check_new_photo_user
from src.handlers.for_admin.send_to_ban_list import (check_ban_callback,
                                                     check_ban_callback_bot,
                                                     check_ban_message_bot)
import src.modules.keyboard as kb

router = Router()


class Registration(StatesGroup):
    name = State()
    nickname = State()
    photo = State()
    city = State()
    gender = State()
    birth_date = State()
    employment = State()
    job_or_study = State()


delete_messages = []
delete_last_message = []


# МЕНЮ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
@router.callback_query(F.data == 'reg')
@check_ban_callback
async def registration(callback: CallbackQuery, state: FSMContext):

    # контрольно убирает состояния если пользователь
    # попал в это меню после удаления анкеты
    await state.clear()

    # получение id пользователя
    user_tg_id = callback.from_user.id

    # проверка наличия пользователя в бд
    data = await asyncio.to_thread(check_user, user_tg_id)

    # если пользователь есть в бд
    if data:

        # уведомление, что вы уже зарегистрированы
        await notification(callback.message, '⚠️ <b>Вы уже зарегистрированы!</b>')

    else:

        # получаю ник пользователя
        user_nickname = callback.from_user.username

        # проверяю наличие id у пользователя
        # (после удаления страницы бывает не подтягивает. Разбираюсь)
        if user_tg_id:

            # проверяю наличие у пользователя ника в телеге
            if user_nickname:

                # удаляю сообщение с кнопкой "зарегистрироваться"
                await del_last_message(callback.message)

                # продолжаю регистрацию если ник есть
                message_to_edit = await callback.message.answer_photo(
                    photo=registration_menu,
                    caption=('<b>✏️📋 Регистрация</b>'
                             '\n\n🟠 Пожалуйста, напишите <b>ваше имя</b>:'),
                    parse_mode='HTML')

                # добавляю id сообщения для дальнейшего редактирования
                await state.update_data(message_to_edit=message_to_edit.message_id)

                # перехожу в состояние регистрации имени
                await state.set_state(Registration.name)

            # если ник в телеге у пользователя не указан
            else:

                # вывожу сообщение о невозможности зарегистрироваться с инструкцией
                await callback.message.answer_video(
                    video=video_no_nickname,
                    caption=('\n\n⚠️ Чтобы продолжить, вам нужно указать \n<b>"Имя пользователя"</b> '
                             'в настройках вашей учетной записи <b>Telegram</b>.\n\n'
                             'Только после этого вы сможете:'),
                    parse_mode='HTML',
                    reply_markup=kb.regkey

                )

        # если id не подтянулся после удаления анкеты
        else:

            # вывожу уведомление с рестартом регистрации
            await callback.message.answer_photo(photo=in_progress,
                                                caption=('Что-то пошло не так :('
                                                         '\nПопробуйте снова чуть позже.'),
                                                parse_mode='HTML',
                                                reply_markup=kb.regkey
                                                )


# ПОЛУЧЕНИЕ ИМЕНИ ПОЛЬЗОВАТЕЛЯ
@router.message(Registration.name)
@check_ban_message_bot
async def get_name(message: Message, state: FSMContext, bot: Bot):

    # удаляю сообщение от пользователя
    await del_last_message(message)

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # завожу проверку на текст и отсутствие смайлов в сообщении
    if message.content_type == 'text' and len(message.text) < 20:

        # сохраняю текст сообщения и привожу его к заглавному
        name = message.text.title()

        # сохраняю ник пользователя
        user_nickname = message.from_user.username

        # проверяю наличие эмодзи в сообщении и markdown разметки
        emodji_checked = await check_emoji(name)
        markdown_checked = await check_all_markdown(name)

        # если эмодзи есть в сообщении
        if emodji_checked or markdown_checked:

            # вывожу уведомление об ошибке
            try:
                await bot.edit_message_media(
                    chat_id=user_tg_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=registration_menu,
                        caption=(
                            '<b>✏️📋 Регистрация</b>'
                            '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                            '\n\n❗️ Имя должно содержать <b>только текст</b>, '
                            'не должно содержать эмодзи, а также '
                            'превышать длинну в <b>20 символов</b>.'
                            '\n\nОтправьте еще раз ваше имя в чат:'),
                        parse_mode='HTML'
                    )
                )
            except Exception as e:
                pass

            # возвращаюсь в состояние ожидания нового сообщения с именем
            return

        # сообщение для редактирования
        message_to_edit = await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b>'
                         '\n\n🟡 Напишите <b>название города</b>, '
                         'в котором вы проживаете:'),
                parse_mode='HTML'
            )
        )

        # добавляю в состояние id особщения для дальнейшего редактирования
        # (а также имя и ник)
        await state.update_data(message_to_edit=message_to_edit.message_id,
                                name=name,
                                nickname=user_nickname)

        # перехожу в состояние регистрации города пользователя
        await state.set_state(Registration.city)

    # если сообщение не текстовое (содержит фото, анимации и т.д.)
    else:

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=registration_menu,
                    caption=(
                        '<b>✏️📋 Регистрация</b>'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Имя не должно содержать изображения или '
                        'любой отличный от текста контент, '
                        'а также превышать длинну в <b>20 символов</b>.'
                        '\n\nОтправьте ваше имя в чат:'
                    ),
                    parse_mode='HTML'
                )
            )
        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания нового сообщения с именем
        return


# ПОЛУЧЕНИЕ НАЗВАНИЕ ГОРОДА ПОЛЬЗОВАТЕЛЯ
@router.message(Registration.city)
@check_ban_message_bot
async def get_city(message: Message, state: FSMContext, bot: Bot):

    # удаляю сообщение пользователя из чата с названием города
    await del_last_message(message)

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # завожу проверку на текст и отсутствие смайлов в сообщении
    if message.content_type == 'text' and len(message.text) < 25:

        # сохраняю текст сообщения и привожу его к заглавному
        city = message.text.title()

        # проверяю наличие эмодзи в сообщении и markdown разметки
        emodji_checked = await check_emoji(city)
        markdown_checked = await check_all_markdown(city)

        # если эмодзи есть в сообщении
        if emodji_checked or markdown_checked:

            # вывожу уведомление об ошибке
            try:
                await bot.edit_message_media(
                    chat_id=user_tg_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=registration_menu,
                        caption=(
                            '<b>✏️📋 Регистрация</b>'
                            '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                            '\n\n❗️ Название города должно содержать '
                            '<b>только текст</b>, не должно содержать эмодзи '
                            'и превышать длинну в <b>25 символов</b>.'
                            '\n\nНапишите название вашего города в чат:'
                        ),
                        parse_mode='HTML'
                    )
                )
            except Exception as e:
                pass

            # возвращаюсь в состояние ожидания нового сообщения с именем
            return

        # сообщение для редактирования
        message_to_edit = await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b>'
                         '\n\n🟢 Укажите <b>ваш пол</b>, выбрав один из вариантов:'),
                parse_mode='HTML'
            ),
            reply_markup=kb.gender
        )

        # сохраняю в состоянии название города и сообщение для редактирования
        await state.update_data(message_to_edit=message_to_edit.message_id, city=city)

        # перехожу в состояние регистрации города пользователя
        await state.set_state(Registration.gender)

    # если сообщение не текстовое (содержит фото, анимации и т.д.)
    else:

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=registration_menu,
                    caption=(
                        '<b>✏️📋 Регистрация</b>'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Название города не должно содержать изображения или '
                        'любой отличный от текста контент, '
                        'а также превышать длинну в <b>25 символов</b>.'
                        '\n\nНапишите название вашего города в чат:'
                    ),
                    parse_mode='HTML'
                )
            )
        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания нового сообщения с именем
        return


# РЕГИСТРАЦИЯ ПОЛА
@router.callback_query(Registration.gender, F.data.in_(['male', 'female', 'other']))
@check_ban_callback
async def get_gender(callback: CallbackQuery, state: FSMContext):

    # сохраняю название пола из колбэка
    gender = callback.data

    # отрисовка страницы
    message_to_edit = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=registration_menu,
            caption=('<b>✏️📋 Регистрация</b>'
                     '\n\n🔵 Напишите в чат <b>дату вашего рождения</b>:'
                     '\n(<i>в формате</i> <b>"ДД.ММ.ГГГГ"</b>'),
            parse_mode='HTML'
        )
    )

    # добавляю название пола в состояние
    await state.update_data(gender=gender,
                            message_to_edit=message_to_edit.message_id)

    # перехожу в состояние регистрации даты рождения
    await state.set_state(Registration.birth_date)


# ПОЛУЧЕНИЕ ДАТЫ РОЖДЕНИЯ
@router.message(Registration.birth_date)
@check_ban_message_bot
async def get_age(message: Message, state: FSMContext, bot: Bot):

    await del_last_message(message)

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # добавляю в список сообщений для удаления данное сообщение
    # delete_messages.append(message.message_id)

    # поверка присланных данных пользователем
    if message.content_type == 'text' and message.text:

        # сообщение от пользователя если прошло проверку на текст
        date_input = message.text

        # проверяю не содержит ли сообщение эмодзи и частично markdown разметку
        emodji_checked = await check_emoji(date_input)
        markdown_checked = await check_partial_markdown(date_input)

        # если содержит эмодзи
        if emodji_checked or markdown_checked:

            # вывожу уведомление об ошибке
            try:
                await bot.edit_message_media(
                    chat_id=user_tg_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=registration_menu,
                        caption=(
                            '<b>✏️📋 Регистрация</b>'
                            '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                            '\n\n❗️ Сообщение должно содержать <b>только дату</b> и '
                            'соответствовать формату: "<b>ДД.ММ.ГГГГ</b>".'
                            '\n(Пример: 01.01.2001)'
                        ),
                        parse_mode='HTML'
                    )
                )
            except Exception as e:
                pass

            # возвращаюсь в состояние ожидания нового сообщения
            return

    # если не содержит эмодзи и markdown разметки-
    # проверяю соответствие формата присланных данных
    # (ДД.ММ.ГГГГ) и реальность даты
    try:

        # проверяю что дата соответствует формату (ДД.ММ.ГГГГ)
        check_birth_date = datetime.strptime(date_input, '%d.%m.%Y')
        user_birth_date = check_birth_date.strftime('%d.%m.%Y')
        today_date = datetime.today()
        user_age = today_date.year - check_birth_date.year - (
            (today_date.month, today_date.day) <
            (check_birth_date.month, check_birth_date.day)
        )

        if user_age < 0 or user_age > 95:

            try:
                await bot.edit_message_media(
                    chat_id=user_tg_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=registration_menu,
                        caption=(
                            '<b>✏️📋 Регистрация</b>'
                            '\n\n⚠️ <b>Ошибка обработки</b> ⚠️'
                            '\n<u>Ваш возраст должен быть в диапазоне</u> '
                            '<u>от 0 до 95 лет</u>'
                            '\n\n❗️ Пришлите действительную дату вашего рождения, '
                            'соотвутствующую формату: "<b>ДД.ММ.ГГГГ</b>".'
                            '\n(Пример: 01.01.2001)'
                        ),
                        parse_mode='HTML'
                    )
                )
            except Exception as e:
                pass

            return

    # если формат неверный
    except:

        # собираю неверные варианты ввода даты для дальнейшего внедрения их редактирования
        await asyncio.to_thread(birth_date_error_catcher, user_tg_id, message.text)

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=registration_menu,
                    caption=(
                        '<b>✏️📋 Регистрация</b>'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Сообщение должно содержать <b>только дату</b> и '
                        'соответствовать формату: "<b>ДД.ММ.ГГГГ</b>".'
                        '\n(Пример: 01.01.2001)'
                    ),
                    parse_mode='HTML'
                )
            )
        except Exception as e:
            pass

        # возвращаю в состояние ожидания нового сообщения с датой
        return

    # если все проверки прошли успешно
    message_to_edit = await bot.edit_message_media(
        chat_id=user_tg_id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=registration_menu,
            caption=('<b>✏️📋 Регистрация</b>'
                     '\n\n🟣 Чем вы занимаетесь?'),
            parse_mode='HTML'
        ),
        reply_markup=kb.check_job_or_study
    )

    # если дата соответствует формату и прошла все проверки -
    # сохраняю ее и высчитанный возраст в состоянии
    await state.update_data(user_birth_date=user_birth_date,
                            user_age=user_age,
                            message_to_edit=message_to_edit.message_id)

    await state.set_state(Registration.employment)


# ПОЛУЧЕНИЕ ДАННЫХ О РАБОТЕ/УЧЕБЕ
@router.callback_query(Registration.employment, F.data.in_(['work', 'study', 'search_myself']))
@check_ban_callback
async def get_job_or_study(callback: CallbackQuery, state: FSMContext):

    # сохраняю данные из колбэка
    employment_data = callback.data

    # отрисовка страницы заполнения данных
    if employment_data == 'work':

        employment_data = 'Работаю'

        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b>'
                         '\n\n⚪️ Напишите коротко <b>кем и в какой сфере вы работаете</b>:'),
                parse_mode='HTML'
            )
        )

        # сохраняю данные колбэка и id сообщения (для редактирования) в состоянии
        await state.update_data(employment_data=employment_data,
                                message_to_edit=message_to_edit.message_id)

        # устанавливаю состояние ввода данных о работе/учебе
        await state.set_state(Registration.job_or_study)

    elif employment_data == 'study':

        employment_data = 'Учусь'

        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b>'
                         '\n\n⚪️ Напишите <b>где и на кого вы учитесь</b>:'),
                parse_mode='HTML'
            )
        )

        # сохраняю данные колбэка и id сообщения (для редактирования) в состоянии
        await state.update_data(employment_data=employment_data,
                                message_to_edit=message_to_edit.message_id)

        # устанавливаю состояние ввода данных о работе/учебе
        await state.set_state(Registration.job_or_study)

    elif employment_data == 'search_myself':

        employment_data = 'В поиске себя'

        in_search_myself = '👀'

        message_to_edit = await callback.message.edit_media(
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b> (<i>последний этап</i> 🤗)'
                         '\n\n📸 Пришлите в чат <b>одно фото</b>, которое будет '
                         'установлено в качестве обложки вашей анкеты:'),
                parse_mode='HTML'
            ),
            reply_markup=kb.late_upload_photo_to_profile
        )

        # сохраняю данные колбэка и id сообщения (для редактирования) в состоянии
        await state.update_data(employment_data=employment_data,
                                work_or_study_info=in_search_myself,
                                message_to_edit=message_to_edit.message_id)

        # устанавливаю состояние регистрации фото
        await state.set_state(Registration.photo)


@router.message(Registration.job_or_study)
@check_ban_message_bot
async def get_info_about_job_or_study(message: Message, state: FSMContext, bot: Bot):

    # удаляю сообщение пользователя из чата с названием города
    await del_last_message(message)

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # TODO ПРОВЕРКА НА ТЕКСТ И СМАЙЛЫ

    # сохраняю данные города из сообщения и привожу название к заглавному

    # завожу проверку на текст и отсутствие смайлов в сообщении
    if message.content_type == 'text':

        # сохраняю текст сообщения и привожу его к заглавному
        work_or_study_info = message.text

        # если сообщение больше 100 символов - обрезаю его и добавляю ... в конце
        if len(message.text) > 100:
            work_or_study_info = work_or_study_info[:100] + '...'

        # проверяю наличие эмодзи и markdown разметки в сообщении
        emodji_checked = await check_emoji(work_or_study_info)
        markdown_checked = await check_partial_markdown(work_or_study_info)

        # если эмодзи есть в сообщении
        if emodji_checked or markdown_checked:

            # вывожу уведомление об ошибке
            try:
                await bot.edit_message_media(
                    chat_id=user_tg_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=registration_menu,
                        caption=(
                            '<b>✏️📋 Регистрация</b>'
                            '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                            '\n\n❗️ Описание должно содержать '
                            '<b>только текст</b>, не должно содержать эмодзи, '
                            'а также превышать длинну в <b>100 символов</b>.'
                            '\n\nОтправьте описание в чат еще раз:'
                        ),
                        parse_mode='HTML'
                    )
                )
            except Exception as e:
                pass

            # возвращаюсь в состояние ожидания нового сообщения с именем
            return

        # если все проверки прошли успешно
        message_to_edit = await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=registration_menu,
                caption=('<b>✏️📋 Регистрация</b> (<i>последний этап</i> 🤗)'
                         '\n\n📸 Пришлите в чат <b>одно фото</b>, которое будет '
                         'установлено в качестве обложки вашей анкеты:'),
                parse_mode='HTML'
            ),
            reply_markup=kb.late_upload_photo_to_profile
        )

        # сохраняю в состоянии название города и сообщение для редактирования
        await state.update_data(message_to_edit=message_to_edit.message_id,
                                work_or_study_info=work_or_study_info)

        # устанавливаю состояние регистрации фото профиля пользователя
        await state.set_state(Registration.photo)

    # если сообщение не текстовое (содержит фото, анимации и т.д.)
    else:

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=registration_menu,
                    caption=(
                        '<b>✏️📋 Регистрация</b>'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\n❗️ Описание не должно содержать изображения или '
                        'любой отличный от текста контент, '
                        'а также превышать длинну в <b>100 символов</b>.'
                        '\n\nОтправьте описание в чат еще раз:'
                    ),
                    parse_mode='HTML'
                )
            )
        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания нового сообщения с именем
        return


# ДОБАВЛЕНИЕ ФОТО И ЗАВЕРШЕНИЕ РЕГИСТРАЦИИ
@router.message(Registration.photo)
@check_ban_message_bot
async def add_photo_to_profile(message: Message, state: FSMContext, bot: Bot):

    await del_last_message(message)

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # поверка что сообщение - фото
    if message.photo:

        # плучаю id фото
        photo_id = message.photo[-1].file_id

        # регистрация нового пользователя и внесение всех необходимых данных в бд
        await sucess_registration(message, state, photo_id, user_tg_id, bot, message_id)

    # если сообщение не фото
    else:

        # вывожу уведомление об ошибке
        try:
            await bot.edit_message_media(
                chat_id=user_tg_id,
                message_id=message_id,
                media=InputMediaPhoto(
                    media=registration_menu,
                    caption=(
                        '<b>✏️📋 Регистрация</b> (<i>последний этап</i> 🤗'
                        '\n\n⚠️ <b>Неверный формат данных</b> ⚠️'
                        '\n\nФото должно быть в формате <b>.jpg '
                        '.jpeg</b> или <b>.png</b>'
                        '\n<i>Отправьте фото в чат:</i>'
                        '\n\n(Вы можете загрузить фото позже, в '
                        'разделе "✏️ <b>Редактировать профиль</b>")'
                    ),
                    parse_mode='HTML'
                ),
                reply_markup=kb.late_upload_photo_to_profile
            )
        except Exception as e:
            pass

        # возвращаюсь в состояние ожидания фото
        return


# ЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕ СТАЛ ДОБАВЛЯТЬ ФОТО И НАЖАЛ "Загрузить позже"
@router.callback_query(F.data == 'late_load_photo')
@check_ban_callback_bot
async def late_upload_photo(callback: CallbackQuery, state: FSMContext, bot: Bot):

    user_tg_id = callback.from_user.id

    # плучаю id сообщения из состояния для его редактирования
    message_to_edit = await state.get_data()
    message_id = message_to_edit.get('message_to_edit')

    # вместо фото от пользователя загружаю "заглушку" об отсутствии фото
    # регистрация нового пользователя и внесение всех необходимых данных в бд
    await sucess_registration(callback.message, state, no_photo_id, user_tg_id, bot, message_id)


# ЛОГИКА ОКОНЧАНИЯ РЕГИСТРАЦИИ
async def sucess_registration(message, state, photo_id, user_tg_id, bot, message_id):

    # получаю текущую дату и время регистрации для внесения в таблицу
    current_datetime = datetime.now()

    # извлекаю данные из состояния
    data = await state.get_data()
    name = data.get('name')
    nickname = data.get('nickname')
    gender = data.get('gender')
    city = data.get('city')
    birth_date = data.get('user_birth_date')
    age = data.get('user_age')
    employment = data.get('employment_data')
    employment_info = data.get('work_or_study_info')

    # передаю данные в функцию добавления нового пользователя в бд
    await asyncio.to_thread(
        add_new_user, current_datetime, user_tg_id, name, photo_id,
        nickname, gender, age, birth_date, city, employment, employment_info
    )

    # отправка фото на модерацию
    if photo_id != no_photo_id:
        info_text = 'Зарегистрирован новый пользователь'
        await check_new_photo_user(photo_id, gender, name, age, city, user_tg_id, bot, info_text)

    # очищаю состояние
    await state.clear()

    # удаляю сообщения из списка для удаления сообщений
    # await del_messages(user_tg_id, delete_messages)

    # уведомление об успешной регистрации
    try:
        await message.edit_media(
            media=InputMediaPhoto(
                media=f'{main_menu_logo}',
                caption=(
                    '<b>Вы успешно зарегистрированы!</b>'
                    '\n\n📌 <b>Добавьте несколько увлечений</b>, чтобы быстрее '
                    'найти интересные контакты и завести новые знакомства!'
                    '\n\n📌 Расскажите более подробно о своём образовании, '
                    'планах, личных качествах (да и вообще о чем угодно), '
                    'заполнив раздел <b>"О себе"</b>.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.start_edit
        )

    except:

        await bot.edit_message_media(
            chat_id=user_tg_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=f'{main_menu_logo}',
                caption=(
                    '<b>Вы успешно зарегистрированы!</b>'
                    '\n\n📌 <b>Добавьте несколько увлечений</b>, чтобы быстрее '
                    'найти интересные контакты и завести новые знакомства!'
                    '\n\n📌 Расскажите более подробно о своём образовании, '
                    'планах, личных качествах (да и вообще о чем угодно), '
                    'заполнив раздел <b>"О себе"</b>.'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.start_edit
        )
