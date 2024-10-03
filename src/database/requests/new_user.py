from src.database.models import get_db_connection

# Проверка наличия ника


async def check_nickname(nickname):

    if not nickname:
        user_nickname = 'пользователь скрыл информацию'

    else:
        user_nickname = f'@{nickname}'

    return user_nickname

# Добавление возраста


def add_new_user(user_tg_id, name, photo_id, nickname, gener, age, birth_date):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        user_tg_id, 
                        name, photo_id, 
                        nickname, gender, 
                        age, 
                        birth_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_tg_id, name, photo_id, nickname, gener, age, birth_date)
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
