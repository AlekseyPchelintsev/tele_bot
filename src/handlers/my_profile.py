from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from src.modules.delete_messages import del_last_message
from src.modules.get_self_data import get_user_info
import src.modules.keyboard as kb


delete_messages = []
delete_last_message = []

router = Router()

# Меню "мой профиль"


@router.callback_query(F.data == 'my_profile')
async def about_me(callback: CallbackQuery, state: FSMContext):

    # получаю свой id
    user_tg_id = callback.from_user.id

    # очищаю состояние
    await state.clear()

    # получаю свои данные для отрисовки страницы
    user_info = await get_user_info(user_tg_id)

    # Извлекаю свои данные для отрисовки страницы
    self_data = user_info['data']
    self_gender = user_info['gender']
    self_hobbies = user_info['hobbies']
    about_me = user_info['about_me']
    # учеба/работа
    employment = user_info['employment']
    employment_info = user_info['employment_info']

    try:

        # отрисовка страницы
        '''await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'► <b>Имя:</b> {self_data[0][0]}'
                    f'\n► <b>Возраст:</b> {self_data[0][4]}'
                    f'\n► <b>Пол:</b> {self_gender}'
                    f'\n► <b>Город:</b> {self_data[0][5]}'
                    f'\n► <b>{employment}:</b> {employment_info}'
                    f'\n► <b>Увлечения:</b> {self_hobbies}'
                    f'\n► <b>О себе:</b> {about_me}'
                    '\n\n<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )'''
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=f'{self_data[0][1]}',
                caption=(
                    f'{self_gender}'  # пол
                    f' • {self_data[0][0]}'  # имя
                    f' • {self_data[0][4]}'  # возраст
                    f' • {self_data[0][5]}'  # город
                    f'\n► <b>{employment}:</b> {employment_info}'
                    f'\n► <b>Увлечения:</b> {self_hobbies}'
                    f'\n► <b>О себе:</b> {about_me}'
                    '\n\n<b>Редактировать:</b>'
                ),
                parse_mode='HTML'
            ),
            reply_markup=kb.about_me
        )

    except:

        try:
            await del_last_message(callback.message)
        except:
            pass

        await callback.message.answer_photo(
            photo=f'{self_data[0][1]}',
            caption=(
                f'{self_gender}'  # пол
                f' • {self_data[0][0]}'  # имя
                f' • {self_data[0][4]}'  # возраст
                f' • {self_data[0][5]}'  # город
                f'\n► <b>Увлечения:</b> {self_hobbies}'
                f'\n► <b>О себе:</b> {about_me}'
                '<b>Редактировать:</b>'
            ),
            parse_mode='HTML',
            reply_markup=kb.about_me
        )
