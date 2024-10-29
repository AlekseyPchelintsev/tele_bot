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

                # получаю основные данные из таблицы users
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

                # получаю данные об увлечениях
                cursor.execute(
                    """
                    SELECT hobby_name 
                    FROM userhobbies 
                    WHERE user_tg_id = %s
                    """,
                    (user_tg_id,)
                )
                user_hobbies = cursor.fetchall()

                # получаю данные "О себе"
                cursor.execute(
                    """
                    SELECT 
                        about_me 
                    FROM aboutme
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )
                user_about_me = cursor.fetchone()

                # получаю данные о роде деятельности
                cursor.execute(
                    """
                    SELECT 
                        work_or_study,
                        work_or_study_info
                    FROM workandstudy
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )
                user_employment = cursor.fetchone()

                data = [(row['name'],
                         row['photo_id'],
                         row['nickname'],
                         row['gender'],
                         row['age'],
                         row['city'])
                        for row in user_data]

                hobbies = [row['hobby_name'] for row in user_hobbies]

                # Преобразуем данные о роде деятельности в кортеж
                employment_data = (
                    user_employment['work_or_study'] if user_employment else '-',
                    user_employment['work_or_study_info'] if user_employment else '-'
                )

                data.append(hobbies)
                data.append(user_about_me['about_me']
                            if user_about_me else '-')
                data.append(employment_data)

                return data
    finally:
        connection.close()
