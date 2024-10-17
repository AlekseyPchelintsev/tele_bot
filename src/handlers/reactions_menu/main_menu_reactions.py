from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from src.modules.get_self_data import get_user_info

import src.modules.keyboard as kb


router = Router()


# Меню реакций
@router.callback_query(F.data == 'all_reactions')
async def all_reactions_menu(callback: CallbackQuery):

    user_tg_id = callback.from_user.id

    # плучаю свои данные
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']

    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'\n<b>Имя:</b> {self_data[0][0]}\n'
                    f'<b>Возраст:</b> {self_data[0][4]}\n'
                    f'<b>Пол:</b> {self_gender}\n'
                    f'<b>Город:</b> {self_data[0][5]}\n'
                    f'<b>Увлечения:</b> {self_hobbies}'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.reactions
        )
    except:
        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'\n<b>Имя:</b> {self_data[0][0]}\n'
                f'<b>Возраст:</b> {self_data[0][4]}\n'
                f'<b>Пол:</b> {self_gender}\n'
                f'<b>Город:</b> {self_data[0][5]}\n'
                f'<b>Увлечения:</b> {self_hobbies}'
            ),
            parse_mode='HTML',
            reply_markup=kb.reactions
        )
