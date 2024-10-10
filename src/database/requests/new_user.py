from src.database.models import get_db_connection

# Проверка наличия ника

'''
async def check_nickname(nickname):

    if not nickname:
        user_nickname = 'пользователь скрыл информацию'

    else:
        user_nickname = f'@{nickname}'

    return user_nickname
'''
# Добавление возраста


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

# Добавление пола


def add_gender(user_tg_id, gender):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users
                    SET gender = %s
                    WHERE user_tg_id = %s
                    """,
                    (gender, user_tg_id)
                )
    finally:
        connection.close()
