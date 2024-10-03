from psycopg2.extras import RealDictCursor
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

# Получение данных конкретного пользователя


def get_user_data(user_tg_id):
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
                        age 
                    FROM users
                    WHERE user_tg_id = %s
                    """,
                    (user_tg_id,)
                )
                user_data = cursor.fetchall()

                cursor.execute(
                    """
                    SELECT hobbie_name 
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
                         row['age'])
                        for row in user_data]

                hobbies = [row['hobbie_name'] for row in user_hobbies]

                data.append(hobbies)

                return data
    finally:
        connection.close()

# Получение данных всех пользователей


def get_data():
    connection = get_db_connection()
    try:
        with connection:
            # cursor_factory=RealDictCursor возвращает кортеж вместо списка
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Выполняем запрос для получения данных пользователей
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id, 
                        name, 
                        photo_id, 
                        nickname, 
                        gender, 
                        age 
                    FROM users
                    """
                )
                user_data = cursor.fetchall()

                # Выполняем запрос для получения данных о хобби
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id, 
                        hobbie_name 
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
                         row['age'])
                        for row in user_data]

                # Формируем словарь хобби
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
        # Закрываем соединение
        connection.close()


# TODO РАЗОБРАТЬСЯ И ВНЕДРИТЬ
'''
def set_user(user_tg_id, name, username, photo_id, gender, age):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT id FROM users WHERE user_tg_id = %s", (user_tg_id,))
                user_id = cursor.fetchone()

                if not user_id:

                    cursor.execute(
                        "INSERT INTO users (user_tg_id, name, user_name, photo_id, gender, age) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user_tg_id, name, username, photo_id, gender, age)
                    )
                    print("Пользователь добавлен в базу данных.")
                else:
                    print("Пользователь уже существует.")
    except Exception as e:
        print(f"Ошибка при выполнении SQL-запроса: {e}")
    finally:
        connection.close()
'''
