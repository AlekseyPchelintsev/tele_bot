from src.database.models import get_db_connection
from src.database.requests.redis_state.redis_get_data import remove_turned_off_user_from_redis, save_users_to_redis


def turn_off_profile(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                # удаляю из таблицы users
                cursor.execute(
                    """
                    UPDATE users
                    SET turn_off_profile = TRUE
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

        # добавляю удалившегося пользователя в redis
        save_users_to_redis()

    except Exception as e:
        print(f'Ошибка удаления анкеты: {e}')
    finally:
        connection.close()


def turn_on_profile(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                # удаляю из таблицы users
                cursor.execute(
                    """
                    UPDATE users
                    SET turn_off_profile = FALSE
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

        # удаляю пользователя включившего профиль из redis
        remove_turned_off_user_from_redis(user_tg_id)

    except Exception as e:
        print(f'Ошибка удаления анкеты: {e}')
    finally:
        connection.close()
