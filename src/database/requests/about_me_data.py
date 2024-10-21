from src.database.models import get_db_connection


# вношу изменения (или добавляю новую запись если записи нет) "О себе"
def edit_about_me_data(user_tg_id, about_me):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO aboutme (user_tg_id, about_me)
                    VALUES (%s, %s)
                    ON CONFLICT (user_tg_id) 
                    DO UPDATE SET about_me = EXCLUDED.about_me
                    """,
                    (user_tg_id, about_me)
                )
    except Exception as e:
        print(f'Ошибка изменения "О себе": {e}')
    finally:
        connection.close()


# удаление текста "О себе"
def delete_about_me_data(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM aboutme
                    WHERE
                        user_tg_id = %s
                    """, (user_tg_id,)
                )
    except Exception as e:
        print(f'Ошибка изменения "О себе": {e}')
    finally:
        connection.close()
