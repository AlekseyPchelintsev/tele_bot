from psycopg2.extras import DictCursor
from src.database.models import get_db_connection


# Добавление реакции в бд и проверка наличия ответной реакции
def insert_reaction(user_tg_id, like_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO userreactions (user_tg_id, like_tg_id)
                        VALUES (%s, %s)
                        ON CONFLICT (user_tg_id, like_tg_id) DO NOTHING;
                    """, (user_tg_id, like_tg_id))
    finally:
        connection.close()


# Удаление реакции из бд
def delete_reaction(user_tg_id, like_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        DELETE FROM userreactions
                        WHERE user_tg_id = %s AND like_tg_id = %s;
                    """, (user_tg_id, like_tg_id))

                return True

    except Exception as e:
        print(f'ОШИБКА УДАЛЕНИЯ ЗАПИСИ: {e}')

    finally:
        connection.close()

# Удаление реакции двух пользователей и добавление в таблицу matchreactions


def delete_and_insert_reactions(user_tg_id, like_tg_id):
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM userreactions
                WHERE user_tg_id = %s AND like_tg_id = %s;
                """, (user_tg_id, like_tg_id))

            cursor.execute(
                """
                DELETE FROM userreactions
                WHERE user_tg_id = %s AND like_tg_id = %s;
                """, (like_tg_id, user_tg_id))

            cursor.execute(
                """
                INSERT INTO matchreactions (user_tg_id_1, user_tg_id_2)
                VALUES (%s, %s), (%s, %s);
                """, (user_tg_id, like_tg_id, like_tg_id, user_tg_id))


# Функция для получения реакции
# Для верной отрисовки кнопки лайка

def get_reaction(user_tg_id, like_tg_id):
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT EXISTS (
                    SELECT 1 FROM userreactions 
                    WHERE user_tg_id = %s AND like_tg_id = %s);
                """, (user_tg_id, like_tg_id))
            return cursor.fetchone()[0]  # Возвращает False, если нет записи


# Получаю данные пользователей, которых я лайкнул


def get_users_with_likes(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT users.*
                    FROM users
                    JOIN userreactions ON users.user_tg_id = userreactions.like_tg_id
                    WHERE userreactions.user_tg_id = %s;
                """, (user_tg_id,)
                )

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
        connection.close()

# Получаю данные пользователей, которые лайкнули меня


def get_users_who_liked_me(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT users.*
                    FROM users
                    JOIN userreactions ON users.user_tg_id = userreactions.user_tg_id
                    WHERE userreactions.like_tg_id = %s;
                """, (user_tg_id,))

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
        connection.close()

#


def get_matches_users_id(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:

                cursor.execute(
                    """
                        SELECT user_tg_id_2
                        FROM matchreactions
                        WHERE user_tg_id_1 = %s
                    """, (user_tg_id,)
                )

                data = cursor.fetchall()

                return data

    finally:
        connection.close()

#


def get_matches_users_data(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT users.*
                    FROM users
                    JOIN matchreactions ON users.user_tg_id = matchreactions.user_tg_id_1
                    WHERE matchreactions.user_tg_id_2 = %s;
                """, (user_tg_id,))

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
        connection.close()

# выводит пользователей в поиске убирая лайкнутых и игнор


def get_liked_users_ids(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:

                # Получаю список пользователей, которых я лайкнул
                cursor.execute(
                    """
                        SELECT like_tg_id
                        FROM userreactions
                        WHERE user_tg_id = %s;
                    """, (user_tg_id,)
                )

                liked_user_ids = cursor.fetchall()

                cursor.execute(
                    '''
                        SELECT user_tg_id_2
                        FROM matchreactions
                        WHERE user_tg_id_1 = %s;
                    ''', (user_tg_id,)
                )

                match_user_ids = cursor.fetchall()

                # Извлекаю только ID пользователей из результата
                liked_user_ids = {row['like_tg_id'] for row in liked_user_ids}
                match_user_ids = {row['user_tg_id_2']
                                  for row in match_user_ids}

                user_tg_ids = liked_user_ids | match_user_ids

                return user_tg_ids
    finally:
        connection.close()

#


def get_ignore_users_ids(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:

                cursor.execute(
                    """
                        SELECT ignore_user_id
                        FROM ignoreusers
                        WHERE user_tg_id = %s;
                    """, (user_tg_id,)
                )

                iam_ignored_ids = cursor.fetchall()

                cursor.execute(
                    """
                        SELECT user_tg_id
                        FROM ignoreusers
                        WHERE ignore_user_id = %s;
                    """, (user_tg_id,)
                )

                me_ignored_ids = cursor.fetchall()

                iam_ignored_ids = {row['ignore_user_id']
                                   for row in iam_ignored_ids}
                me_ignored_ids = {row['user_tg_id']
                                  for row in me_ignored_ids}

                ignore_list_ids = iam_ignored_ids | me_ignored_ids

                return ignore_list_ids

    except Exception as e:
        print(f'ОШИБКА ПОЛУЧЕНИЯ IGNORE LIST IDS: {e}')

    finally:
        connection.close()

#


def get_my_ignore_list_users(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:

                cursor.execute("""
                    SELECT users.*
                    FROM users
                    JOIN ignoreusers ON users.user_tg_id = ignoreusers.ignore_user_id
                    WHERE ignoreusers.user_tg_id = %s;
                """, (user_tg_id,)
                )

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

    except Exception as e:
        print(f'ОШИБКА ПОЛУЧЕНИЯ IGNORE LIST USERS: {e}')

    finally:
        connection.close()

#


def check_matches_two_users(user_tg_id, like_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM userreactions 
                    WHERE (user_tg_id = %s AND like_tg_id = %s) 
                       OR (user_tg_id = %s AND like_tg_id = %s);
                    """, (user_tg_id, like_tg_id, like_tg_id, user_tg_id)
                )
                count = cursor.fetchone()[0]
                return count == 2
    finally:
        connection.close()

#


def send_user_to_ignore_table(user_tg_id, like_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO ignoreusers (user_tg_id, ignore_user_id)
                        VALUES (%s, %s)
                        ON CONFLICT (user_tg_id, ignore_user_id) DO NOTHING;
                    """, (user_tg_id, like_tg_id)
                )
    finally:
        connection.close()

#


def delete_from_my_contacts(user_tg_id, like_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM matchreactions
                    WHERE (user_tg_id_1 = %s AND user_tg_id_2 = %s)
                    OR (user_tg_id_1 = %s AND user_tg_id_2 = %s)
                    """, (user_tg_id, like_tg_id, like_tg_id, user_tg_id)
                )
                return True

    except Exception as e:
        print(f'ОШИБКА УДАЛЕНИЯ КОНТАКТА: {e}')

    finally:
        connection.close()

#


def remove_user_from_ignore_table(user_tg_id, current_user_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM ignoreusers
                    WHERE (user_tg_id = %s AND ignore_user_id = %s)
                    """, (user_tg_id, current_user_id)
                )

                return True

    except Exception as e:
        print(f'ОШИБКА УДАЛЕНИЯ ИЗ IGNORE LIST: {e}')

    finally:
        connection.close()
