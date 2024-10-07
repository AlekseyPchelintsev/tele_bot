from psycopg2.extras import RealDictCursor
from src.database.models import get_db_connection


# ----- ПОИСК ПО ХОББИ -----

# Проверка наличия пользователей по хобби в таблице userhobbies


def check_users_by_hobby(hobby_name, user_tg_id):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_tg_id
                    FROM userhobbies
                    WHERE hobby_name = %s AND user_tg_id != %s
                    """, (hobby_name, user_tg_id)
                )
                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()

# Выборка пользователей по хобби из таблицы userhobbies


def get_users_by_hobby(hobby, user_tg_id, gender_data):
    connection = get_db_connection()

    user_tg_ids_hobby = check_users_by_hobby(hobby, user_tg_id)
    user_tg_ids_gender = check_users_by_gender(user_tg_id, gender_data)

    try:
        user_tg_ids = set(user_tg_ids_hobby) & set(user_tg_ids_gender)
    except:
        return

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
                            nickname, 
                            gender, 
                            age,
                            city
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (list(user_tg_ids),)
                    )
                    user_data = cursor.fetchall()

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

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['nickname'],
                             row['gender'],
                             row['age'],
                             row['city'])
                            for row in user_data]

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

# ----- ПОИСК ПО ГОРОДУ -----

# Проверка наличия пользователей в городе


def check_users_in_city(user_tg_id):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT city
                    FROM users
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

                user_city = cursor.fetchone()
                user_city_row = user_city[0]

                cursor.execute(
                    """
                    SELECT user_tg_id
                    FROM users
                    WHERE city = %s AND user_tg_id != %s
                    """, (user_city_row, user_tg_id)
                )
                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()

# Выборка пользователей по городу пользователя


def get_users_in_city(user_tg_id, gender_data):
    connection = get_db_connection()

    user_tg_ids_city = check_users_in_city(user_tg_id)

    # Получаем список user_tg_ids по полу
    user_tg_ids_gender = check_users_by_gender(user_tg_id, gender_data)

    # Пересекаем списки user_tg_ids
    try:
        user_tg_ids = set(user_tg_ids_city) & set(user_tg_ids_gender)
    except:
        return

    # Если пересеченный список пуст, возвращаем None

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
                            nickname, 
                            gender, 
                            age,
                            city
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (list(user_tg_ids),)
                    )
                    user_data = cursor.fetchall()

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

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['nickname'],
                             row['gender'],
                             row['age'],
                             row['city'])
                            for row in user_data]

                hobbies = {}

                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobbie_name = row['hobby_name']
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


# ----- ПОИСК ПО ПОЛУ -----

# Проверка наличия пользователей определенного пола


def check_users_by_gender(user_tg_id, gender_data):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                if gender_data == 'all':
                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE user_tg_id != %s
                        """, (user_tg_id,)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE gender = %s AND user_tg_id != %s
                        """, (gender_data, user_tg_id)
                    )

                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()


def get_users_by_gender(user_tg_id, gender_data):
    connection = get_db_connection()
    user_tg_ids = check_users_by_gender(user_tg_id, gender_data)

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
                            nickname, 
                            gender, 
                            age,
                            city
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (user_tg_ids,)
                    )
                    user_data = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id,
                            hobby_name
                        FROM userhobbies
                        WHERE user_tg_id = ANY(%s)   
                        """, (user_tg_ids,)
                    )
                    hobbies_data = cursor.fetchall()

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['nickname'],
                             row['gender'],
                             row['age'],
                             row['city'])
                            for row in user_data]

                hobbies = {}

                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobbie_name = row['hobby_name']
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
