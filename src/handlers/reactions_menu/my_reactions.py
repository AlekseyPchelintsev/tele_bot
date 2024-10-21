import asyncio
from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.pagination_logic import load_pagination_start_or_end_data, back_callback
from src.database.requests.likes_users import get_users_with_likes
from src.modules.notifications import attention_message


router = Router()


# Мои реакции
@router.callback_query(F.data == 'my_reactions')
async def my_reactions(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    data = await asyncio.to_thread(get_users_with_likes, user_tg_id)

    # если False (данные отсутствуют)
    if not data:

        # выводим сообщение об отсутствии реакций
        text_info = '<b>Список реакций пуст</b> 🤷‍♂️'
        await back_callback(callback.message,
                            user_tg_id,
                            'back_reactions',
                            'reactions',
                            text_info)

    # если True (есть данные)
    else:

        total_pages = len(data)

        await load_pagination_start_or_end_data(callback.message,
                                                data,
                                                'paginator_likes',
                                                'my_like_users',
                                                total_pages)

        if total_pages == 1:

            await attention_message(callback.message, '<b>В списке всего 1 пользователь</b>', 2)

        await state.update_data(users_data=data)
