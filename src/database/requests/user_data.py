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

                cursor.execute(
                    """
                    SELECT 
                        about_me 
                    FROM aboutme
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )
                user_about_me = cursor.fetchone()

                data = [(row['name'],
                         row['photo_id'],
                         row['nickname'],
                         row['gender'],
                         row['age'],
                         row['city'])
                        for row in user_data]

                hobbies = [row['hobby_name'] for row in user_hobbies]

                data.append(hobbies)
                data.append(user_about_me['about_me']
                            if user_about_me else '-')

                return data
    finally:
        connection.close()
