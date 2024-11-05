from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from config import reactions_menu_logo

import src.modules.keyboard as kb


router = Router()


# Меню реакций
@router.callback_query(F.data == 'all_reactions')
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


# Меню реакций через обычную клавиатуру
@router.message(F.text == '👋 Мои реакции')
async def all_reactions_menu(message: Message, state: FSMContext):

    # очищаю состояние
    await state.clear()

    # отрисовка страницы
    try:
        await message.edit_media(
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
        await message.answer_photo(
            photo=f'{reactions_menu_logo}',
            caption=(
                '<b>Раздел ваших реакций:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.reactions
        )
