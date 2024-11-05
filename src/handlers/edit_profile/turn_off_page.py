import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from src.database.requests.turn_off_on_profile import turn_off_profile, turn_on_profile
from src.database.requests.redis_state.redis_get_data import redis_client
from config import delete_profile_id, on_profile, off_profile

import src.modules.keyboard as kb

router = Router()


# отключение своей анкеты
@router.callback_query(F.data == 'stop_profile')
async def turn_off_profile_by_user(callback: CallbackQuery, state: FSMContext):

    # сооббщение об удалении анкеты
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=delete_profile_id,
            caption=(
                '<b>Вы уверены?</b>'
                '\n\nДругие пользователи не смогут увидеть вашу анкету в поиске, '
                'а вы не сможете взаимодействовать с сервисом, пока снова '
                'не активируете свой профиль.'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.turn_off_profile
    )

    # сохраняю id сообщения чтобы потом его удалить
    await state.update_data(message_id=edit_message.message_id)


# подтверждение отключения анкеты
@router.callback_query(F.data == 'confirm_turn_off')
async def confirm_turning_off_profile(callback: CallbackQuery, state: FSMContext, bot: Bot):

    # плучаю свой id
    user_tg_id = callback.from_user.id

    # получаю id особщения для редактирования/удаления
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # удаляю данные пользовтеля из таблицы users
    await asyncio.to_thread(turn_off_profile, user_tg_id)

    # удаляю сообщение с подтверждением удаления из чата
    try:
        await bot.delete_message(chat_id=user_tg_id, message_id=message_id)
    except:
        pass

    # удаление реплай клавиатуры
    await callback.message.answer_photo(
        photo=off_profile,
        caption=(
            '<b>Ваша страница отключена.</b>'
            '\n\nЧто бы вернуть возможность взаимодействия с сервисом и '
            'снова стать видимым в поиске для других пользователей - '
            'отправьте в чат команду <b>"Включить профиль"</b> или воспользуйтесь '
            'специальной клавиатурой ниже.'),
        parse_mode='HTML',
        reply_markup=kb.profile_are_off
    )


# включение анкеты
turn_on_commands = ['🔌 Включить профиль',
                    'Включить профиль', 'включить профиль']


@router.message(F.text.in_(turn_on_commands), flags={"allow_turned_off_users": True})
async def turn_on_profile_by_user(message: Message, bot: Bot):

    # получаю id пользователя
    user_tg_id = message.from_user.id

    # получаю данные отключенных пользователей из redis
    check_turn_off_users = redis_client.smembers('turn_off_users')

    # проверяю наличие пользователя в redis для отключения этой
    # команды для тех кто не блокировал свой профиль
    if str(user_tg_id) in check_turn_off_users:

        # включаю страницу и удаляю из redis
        await asyncio.to_thread(turn_on_profile, user_tg_id)

        # отправляю уведомление о включении страницы и клавиатуру с главным меню
        await bot.send_photo(
            chat_id=user_tg_id,
            photo=on_profile,
            caption=('<b>Рады что вы вернулись!</b>'
                     '\n\n☑️ Взаимодействие с сервисом восстановлено.'
                     '\n☑️ Ваша анкета снова доступна в поиске другим пользователям.'),
            parse_mode='HTML',
            reply_markup=kb.users
        )

    else:
        return
