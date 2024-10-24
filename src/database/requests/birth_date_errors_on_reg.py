from src.database.models import get_db_connection


def birth_date_error_catcher(user_tg_id, input_date):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                        INSERT INTO birthdateerror (user_tg_id, wrong_birth_date)
                        VALUES (%s, %s)
                     """, (user_tg_id, input_date)
                )

    finally:
        connection.close()
