import asyncio
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from src.database.requests.delete_profile import delete_profile
from config import delete_profile_id

import src.modules.keyboard as kb

router = Router()


# удаление своей анкеты

@router.callback_query(F.data == 'delete_profile')
async def delete_my_profile(callback: CallbackQuery, state: FSMContext):

    # сооббщение об удалении анкеты
    edit_message = await callback.message.edit_media(
        media=InputMediaPhoto(
            media=f'{delete_profile_id}',
            caption=(
                '<b>Вы уверены?</b>'
            ),
            parse_mode='HTML'
        ),
        reply_markup=kb.delete_profile
    )

    # сохраняю id сообщения чтобы потом его удалить
    await state.update_data(message_id=edit_message.message_id)


# подтверждение удаления анкеты

@router.callback_query(F.data == 'confirm_delete')
async def confirm_delete(callback: CallbackQuery, state: FSMContext, bot: Bot):

    # плучаю свой id
    user_tg_id = callback.from_user.id

    # получаю id особщения для редактирования/удаления
    message_data = await state.get_data()
    message_id = message_data.get('message_id')

    # удаляю данные пользовтеля из таблицы users
    await asyncio.to_thread(delete_profile, user_tg_id)

    # удаляю сообщение с подтверждением удаления из чата
    await bot.delete_message(chat_id=user_tg_id, message_id=message_id)

    # ввыожу сообщение о необходимости зарегистрироваться после удаления анкеты
    await callback.message.answer(text='Для начала вам нужно:',
                                  reply_markup=kb.regkey)
