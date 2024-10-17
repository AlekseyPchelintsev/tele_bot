from src.database.models import get_db_connection
from psycopg2.extras import RealDictCursor


def render_users(user_tg_ids):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return []

                # Получаем данные пользователей
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id, 
                        name, 
                        photo_id, 
                        nickname, 
                        gender, 
                        age,
                        city
                    FROM users 
                    WHERE user_tg_id = ANY(%s)
                    """, (list(user_tg_ids),)
                )
                user_data = cursor.fetchall()

                # Получаем хобби пользователей
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id,
                        hobby_name
                    FROM userhobbies
                    WHERE user_tg_id = ANY(%s)   
                    """, (list(user_tg_ids),)
                )
                hobbies_data = cursor.fetchall()

                # Формируем список данных пользователей
                data = [(row['user_tg_id'],
                         row['name'],
                         row['photo_id'],
                         row['nickname'],
                         row['gender'],
                         row['age'],
                         row['city'])
                        for row in user_data]

                # Собираем хобби пользователей
                hobbies = {}
                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobby_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobby_name)

                # Добавляем список хобби к данным пользователей
                for i in range(len(data)):
                    user_tg_id = data[i][0]  # Извлекаем user_tg_id
                    hobbies_list = hobbies.get(
                        user_tg_id)  # Получаем список хобби
                    data[i] = (*data[i], hobbies_list)

                return data
    finally:
        connection.close()
