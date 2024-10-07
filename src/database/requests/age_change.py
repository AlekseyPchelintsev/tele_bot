from src.database.models import get_db_connection


def change_user_age(user_tg_id, user_age, user_birth_date):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users 
                    SET 
                        age = %s,
                        birth_date = %s
                    WHERE user_tg_id = %s
                    """,
                    (user_age, user_birth_date,  user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка изменения даты рождения: {e}')
    finally:
        connection.close()
