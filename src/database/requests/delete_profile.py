from src.database.models import get_db_connection


def delete_profile(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM users 
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

    except Exception as e:
        print(f'Ошибка удаления анкеты: {e}')
    finally:
        connection.close()
