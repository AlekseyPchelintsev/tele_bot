from psycopg2.extras import RealDictCursor
from src.database.requests.likes_users import get_ignore_users_ids
from src.database.requests.likes_users import get_liked_users_ids
from src.database.models import get_db_connection


# ----- ОБРАБОТКА ДАННЫХ ПОЛЬЗОВАТЕЛЯ(ЕЙ) -----

# Проверка регистрации пользователя


def check_user(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT user_tg_id 
                    FROM users 
                    WHERE user_tg_id = %s
                    """,
                    (user_tg_id,)
                )
                user_id = cursor.fetchone()

                if user_id:
                    cursor.execute(
                        """
                        SELECT name 
                        FROM users 
                        WHERE user_tg_id = %s
                        """,
                        (user_tg_id,)
                    )

                    user_name = cursor.fetchone()
                    data = (user_id[0], user_name[0])

                    return data

                else:
                    return
    finally:
        connection.close()

# Получение моих данных


def get_self_data(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:

                cursor.execute(
                    """
                    SELECT 
                        name, 
                        photo_id, 
                        nickname, 
                        gender, 
                        age,
                        city
                    FROM users
                    WHERE user_tg_id = %s
                    """,
                    (user_tg_id,)
                )
                user_data = cursor.fetchall()

                cursor.execute(
                    """
                    SELECT hobby_name 
                    FROM userhobbies 
                    WHERE user_tg_id = %s
                    """,
                    (user_tg_id,)
                )
                user_hobbies = cursor.fetchall()

                data = [(row['name'],
                         row['photo_id'],
                         row['nickname'],
                         row['gender'],
                         row['age'],
                         row['city'])
                        for row in user_data]

                hobbies = [row['hobby_name'] for row in user_hobbies]

                data.append(hobbies)

                return data
    finally:
        connection.close()

# Получение данных всех пользователей дя поиска all_users


def get_all_users_data(self_tg_id, gender_data):

    connection = get_db_connection()

    # получаю списки пользователей для исключения
    ignore_users_ids = get_ignore_users_ids(self_tg_id)
    liked_users_ids = get_liked_users_ids(self_tg_id)

    # объединяю оба множества
    ignore_list = ignore_users_ids | liked_users_ids

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Начинаем формировать запрос
                base_query = """
                    SELECT 
                        user_tg_id, 
                        name, 
                        photo_id, 
                        nickname, 
                        gender, 
                        age,
                        city
                    FROM users
                    WHERE user_tg_id != %s
                """
                params = [self_tg_id]

                # Если передан список для исключения, добавляем условие
                if ignore_list:

                    # Создаю плейсхолдеры
                    placeholders = ', '.join(['%s'] * len(ignore_list))
                    base_query += f" AND user_tg_id NOT IN ({placeholders})"
                    params.extend(ignore_list)

                # Если gender_data не 'all', добавляем условие по полу
                if gender_data != 'all':
                    base_query += " AND gender = %s"
                    params.append(gender_data)

                cursor.execute(base_query, params)
                user_data = cursor.fetchall()

                # Выполняем запрос для получения данных о хобби
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id, 
                        hobby_name 
                    FROM userhobbies
                    """
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

                # Формируем словарь хобби
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
        # Закрываем соединение
        connection.close()
