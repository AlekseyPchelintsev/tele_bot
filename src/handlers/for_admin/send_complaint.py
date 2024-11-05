import src.handlers.for_admin.admin_keyboards as kb_admin
from config import complaint_chat_id
from src.modules.get_self_data import get_user_info


async def send_complaint(complaint_user_id,
                         bot,
                         info_text=''):

    # получаю данные пользователя из бд
    user_info = await get_user_info(complaint_user_id)

    # формирую информацию о пользователе
    user_data = user_info['data']
    user_photo = user_data[0][1]
    user_name = user_data[0][0]
    user_age = user_data[0][4]
    user_city = user_data[0][5]
    user_gender = user_info['gender']
    user_hobbies = user_info['hobbies']
    user_about_me = user_info['about_me']
    employment = user_info['employment']
    employment_info = user_info['employment_info']

    await bot.send_photo(
        chat_id=complaint_chat_id,
        photo=user_photo,
        caption=(
            f'<b>{info_text}</b>'
            f'\n\n<b>id пльзователя:</b> {complaint_user_id}'
            f'\n\n{user_gender}'  # пол
            f' • {user_name}'  # имя
            f' • {user_age}'  # возраст
            f' • {user_city}'  # город
            f'\n► <b>{employment}:</b> {employment_info}'
            f'\n► <b>Увлечения:</b> {user_hobbies}'
            f'\n► <b>О себе:</b> {user_about_me}'
        ),
        parse_mode='HTML',
        reply_markup=kb_admin.get_complaint(complaint_user_id)
    )
