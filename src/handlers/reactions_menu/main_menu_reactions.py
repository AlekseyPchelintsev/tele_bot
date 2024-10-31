from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from config import reactions_menu_logo
from src.handlers.for_admin.send_to_ban_list import check_ban_callback

import src.modules.keyboard as kb


router = Router()


# Меню реакций
@router.callback_query(F.data == 'all_reactions')
@check_ban_callback
async def all_reactions_menu(callback: CallbackQuery, state: FSMContext):

    # отрисовка страницы
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{reactions_menu_logo}',
                caption=(
                    '<b>Раздел ваших реакций:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.reactions
        )
    except:
        await callback.message.answer_photo(
            photo=f'{reactions_menu_logo}',
            caption=(
                '<b>Раздел ваших реакций:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.reactions
        )
