from src.database.models import get_db_connection


def change_user_name(user_tg_id, user_name):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users 
                    SET name = %s 
                    WHERE user_tg_id = %s
                    """,
                    (user_name, user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка изменения имени: {e}')
    finally:
        connection.close()
