from psycopg2.extras import RealDictCursor
from src.database.models import get_db_connection


# ----- ПОИСК ПО ХОББИ -----

# Проверка наличия пользователей по хобби в таблице userhobbies


def check_users_by_hobby(hobby_name):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_tg_id
                    FROM userhobbies
                    WHERE hobbie_name = %s
                    """, (hobby_name,)
                )
                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()

# Выборка пользователей по хобби из таблицы userhobbies


def get_users_by_hobby(hobby):
    connection = get_db_connection()
    user_tg_ids = check_users_by_hobby(hobby)

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return
                else:
                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id, 
                            name, 
                            photo_id, 
                            user_name, 
                            gender, 
                            age 
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (user_tg_ids,)
                    )
                    user_data = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id,
                            hobbie_name
                        FROM userhobbies
                        WHERE user_tg_id = ANY(%s)   
                        """, (user_tg_ids,)
                    )
                    hobbies_data = cursor.fetchall()

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['user_name'],
                             row['gender'],
                             row['age'])
                            for row in user_data]

                hobbies = {}

                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobbie_name = row['hobbie_name']
                    hobbies.setdefault(user_tg_id, []).append(hobbie_name)

                # Добавляем список хобби к данным пользователей
                for i in range(len(data)):
                    user_tg_id = data[i][0]  # Извлекаем user_tg_id
                    hobbies_list = hobbies.get(
                        user_tg_id)  # Получаем список хобби
                    data[i] = (*data[i], hobbies_list)

                return data
    finally:
        connection.close()
