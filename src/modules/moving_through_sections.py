from src.handlers.my_profile import about_me
from src.handlers.reactions_menu.main_menu_reactions import all_reactions_menu
from src.handlers.search_users.search_users_menu import check_users_menu


async def check_menu_command(user_tg_id, message, feedback_from_user, state):

    # мипорт внутри функции для избежания циклических зависимостей
    # в разделе обратной связи с администратором
    from src.handlers.for_admin.feedback_from_users import feedback_menu

    await state.clear()

    if feedback_from_user == '🔎 Найти пользователей':
        await check_users_menu(message, state)
    elif feedback_from_user == '👋 Мои реакции':
        await all_reactions_menu(message, state)
    elif feedback_from_user == '✏️ Редактировать профиль':
        await about_me(message, state)
    elif feedback_from_user == '📬 Оставить отзыв':
        await feedback_menu(message, state)
