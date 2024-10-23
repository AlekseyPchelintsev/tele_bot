from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from config import reactions_menu_logo

import src.modules.keyboard as kb


router = Router()


# Меню реакций
@router.callback_query(F.data == 'all_reactions')
async def all_reactions_menu(callback: CallbackQuery):

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
