from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_last_message
from src.modules.get_self_data import get_user_info
import src.modules.keyboard as kb

router = Router()


@router.callback_query(F.data == 'main_menu')
async def open_main_menu(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние
    await state.clear()

    # получаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']

    try:

        # отрисовка страницы
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
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
            photo=f'{self_data[0][1]}',
            caption=(
                '<b>Главное меню:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.users
        )
