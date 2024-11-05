from psycopg2.extras import DictCursor
from src.database.models import get_db_connection
from src.database.requests.check_turn_off_or_ban import get_turn_off_users, get_users_in_ban


# IDs ПОЛЬЗОВАТЕЛЕЙ НА ИСКЛЮЧЕНИЕ ИЗ ПОИСКА

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


# общая функция обработчик
def get_exclude_users_ids(user_tg_id):

    # получаю множества пользователей для исключения
    ignore_users_ids = get_ignore_users_ids(user_tg_id)
    liked_users_ids = get_liked_users_ids(user_tg_id)
    # предварительно преобразую в множества (функции возвращают списки)
    turned_off_users = set(get_turn_off_users())
    banned_users = set(get_users_in_ban())

    # объединяю оба множества
    ignore_list = ignore_users_ids | liked_users_ids | turned_off_users | banned_users

    return ignore_list
