from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_last_message
from config import main_menu_logo
import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'main_menu')
async def open_main_menu(callback: CallbackQuery, state: FSMContext):

    # очищаю состояние (на всякий случай)
    await state.clear()

    try:

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{main_menu_logo}',
                caption=(
                    '<b>Главное меню:</b>'

                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.users
        )
    except:

        try:
            await del_last_message(callback.message)
        except:
            pass

        await callback.message.answer_photo(
            photo=f'{main_menu_logo}',
            caption=(
                '<b>Главное меню:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.users
        )
