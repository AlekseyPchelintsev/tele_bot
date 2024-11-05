from src.database.requests.redis_state.redis_get_data import remove_unbaned_user_from_redis, save_users_to_redis
from src.database.models import get_db_connection


# бан пользователя
def ban_user(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # добавляю пользователя в бан
                cursor.execute(
                    """
                    UPDATE users
                    SET ban_status = TRUE
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

        # добавляю забаненного в redis
        save_users_to_redis()

    except Exception as e:
        print(f'Ошибка добавления в бан: {e}')

    finally:
        connection.close()


# разбан пользователя
def unban_user(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # добавляю пользователя в бан
                cursor.execute(
                    """
                    UPDATE users
                    SET ban_status = FALSE
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

        remove_unbaned_user_from_redis(user_tg_id)

    except Exception as e:
        print(f'Ошибка добавления в бан: {e}')

    finally:
        connection.close()
