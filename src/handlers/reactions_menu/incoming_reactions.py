import asyncio
from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.pagination_logic import load_pagination_start_or_end_data, back_callback
from src.database.requests.likes_users import get_users_who_liked_me
from src.modules.notifications import attention_message


router = Router()


# Входящие реакции
@router.callback_query(F.data == 'incoming_reactions_list')
async def my_reactions(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_users_who_liked_me, user_tg_id)

    # если False (данные отсутствуют)
    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>Входящих реакций пока что нет</b> 😔'
        await back_callback(callback.message,
                            'back_reactions',
                            'reactions',
                            text_info=text_info)

    # если True (есть данные)
    else:

        total_pages = len(data)

        # если найден всего 1 пользователь
        if total_pages == 1:
            text_info = '\n\n<b>📍 В списке всего 1 пользователь</b>'
        else:
            text_info = ''

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'incoming_reactions',
                                                'incoming_like_users',
                                                total_pages,
                                                text_info)

        await state.update_data(users_data=data)
