from src.database.models import get_db_connection


def change_user_gender(user_tg_id, gender):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users 
                    SET 
                        gender = %s
                    WHERE user_tg_id = %s
                    """,
                    (gender, user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка изменения пола: {e}')
    finally:
        connection.close()
