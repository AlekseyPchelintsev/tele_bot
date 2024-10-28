from src.database.models import get_db_connection


def change_user_employment(user_tg_id, employment, employment_info):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE workandstudy 
                    SET 
                        work_or_study = %s,
                        work_or_study_info = %s
                    WHERE user_tg_id = %s
                    """,
                    (employment, employment_info, user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка изменения пола: {e}')
    finally:
        connection.close()
