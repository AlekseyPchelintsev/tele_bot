from src.database.models import get_db_connection


def change_city(new_city, user_tg_id):

    connection = get_db_connection()
    new_city = new_city.title()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users
                    SET city = %s
                    WHERE user_tg_id = %s
                    """, (new_city, user_tg_id)
                )
    finally:
        connection.close()
