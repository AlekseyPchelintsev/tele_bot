import asyncio
from src.database.requests.user_data import get_self_data
from src.modules.check_gender import check_gender
from src.modules.hobbies_list import hobbies_list


# ПОЛУЧАЮ СВОИ ДАННЫЕ ИЗ БД

async def get_user_info(user_tg_id):

    # Получаю свои данные из бд
    self_data = await asyncio.to_thread(get_self_data, user_tg_id)

    # Извлекаю и обрабатыва необходимые данные
    self_gender = await check_gender(self_data[0][3])
    self_hobbies = await hobbies_list(self_data[1])

    # Возвращаю данные в виде словаря
    return {
        'data': self_data,
        'gender': self_gender,
        'hobbies': self_hobbies
    }
