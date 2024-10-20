from src.database.models import get_db_connection


# Добавление нового пользователя

def add_new_user(date_time, user_tg_id, name, photo_id, nickname, gener, age, birth_date, city):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        date_time,
                        user_tg_id, 
                        name, 
                        photo_id, 
                        nickname,
                        gender, 
                        age, 
                        birth_date,
                        city)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (date_time, user_tg_id, name, photo_id, nickname,
                     gener, age, birth_date, city)
                )
    finally:
        connection.close()
