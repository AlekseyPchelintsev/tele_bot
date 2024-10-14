import asyncio
from src.database.requests.user_data import get_user_data
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list


async def get_user_info(user_tg_id):
    # Получаем данные пользователя в отдельном потоке
    self_data = await asyncio.to_thread(get_user_data, user_tg_id)

    # Извлекаем необходимые данные
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

    # Возвращаем данные в виде словаря
    return {
        'data': self_data,
        'gender': self_gender,
        'hobbies': self_hobbies
    }
