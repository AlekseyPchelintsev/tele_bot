from src.database.models import get_db_connection


def change_user_employment(user_tg_id, employment, employment_info):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO workandstudy (user_tg_id, work_or_study, work_or_study_info)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_tg_id) 
                    DO UPDATE SET 
                        work_or_study = EXCLUDED.work_or_study,
                        work_or_study_info = EXCLUDED.work_or_study_info
                    """,
                    (user_tg_id, employment, employment_info)
                )

    except Exception as e:
        print(f'Ошибка изменения пола: {e}')
    finally:
        connection.close()
