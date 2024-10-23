from psycopg2.extras import DictCursor
from src.database.requests.render_users import render_users
from src.database.models import get_db_connection


# IDs ПОЛЬЗОВАТЕЛЕЙ НА ИСКЛЮЧЕНИЕ ИЗ ПОИСКАА

# кого уже лайкнул и с кем взаимные реакции
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

                # получаю список пользователей с взаимными реакциями
                cursor.execute(
                    '''
                        SELECT user_tg_id_2
                        FROM matchreactions
                        WHERE user_tg_id_1 = %s;
                    ''', (user_tg_id,)
                )

                match_user_ids = cursor.fetchall()

                # создаю множества чтобы исключить дубликаты (на всякий случай)
                liked_user_ids = {row['like_tg_id'] for row in liked_user_ids}
                match_user_ids = {row['user_tg_id_2']
                                  for row in match_user_ids}

                # объединяю в одно множество
                user_tg_ids = liked_user_ids | match_user_ids

                return user_tg_ids
    finally:
        connection.close()


# кого заблокировал и кто заблокировал меня
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

# =============================================================================


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
# для отображения в "мои контакты"
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


# Функция для проверки наличия актуальной реакции в бд от пользователя (если еще не удалил)
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
                result = render_users([user[0] for user in user_data])

                return result
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
                result = render_users([user[0] for user in user_data])

                return result
    finally:
        connection.close()


# получаю id пльзователей из списка "мои контакты"
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


# получаю данные пользователей из списка "мои контакты"
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
                result = render_users([user[0] for user in user_data])

                return result

    finally:
        connection.close()


# для отображения списка заблокированных мною пользователей в "заблокированные пользователи"
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
                result = render_users([user[0] for user in user_data])

                return result

    except Exception as e:
        print(f'ОШИБКА ПОЛУЧЕНИЯ IGNORE LIST USERS: {e}')

    finally:
        connection.close()


# проверка ответной реакции от пользователя которого я лайнклу
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


# отклонение входящей реакции и добавление пользователя в "заблокированные пользователи"
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

                cursor.execute(
                    """
                        DELETE FROM userreactions
                        WHERE user_tg_id = %s AND like_tg_id = %s
                    """, (like_tg_id, user_tg_id)
                )
    finally:
        connection.close()


# удаление пользователя из "моих контактов" и добавление в "заблокированные пользователи"
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


# удаление пользователя из списка "заблокированных пользователей"
# чтобы он выводился в поиске (и я у него)
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
