from src.database.models import get_db_connection


# плучаю id удалившихся пользователей
def get_turn_off_users():

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                        SELECT user_tg_id
                        FROM users
                        WHERE turn_off_profile = TRUE
                    """
                )

                data_check = cursor.fetchall()

                return [user_tg_id for (user_tg_id,) in data_check]

    except Exception as e:
        print(f'Ошибка получения бан лисита: {e}')

    finally:
        connection.close()


# получаю id забаненых пользователей
def get_users_in_ban():

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                        SELECT user_tg_id
                        FROM users
                        WHERE ban_status = TRUE 
                    """
                )

                data_check = cursor.fetchall()

                return [user_tg_id for (user_tg_id,) in data_check]

    except Exception as e:
        print(f'Ошибка получения бан лисита: {e}')

    finally:
        connection.close()
