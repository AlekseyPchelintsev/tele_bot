from config import no_photo_id
from src.database.models import get_db_connection

# Проверка наличия фото при регистрации


async def check_user_photo(user_photo):

    if not user_photo:
        photo_id = no_photo_id

    else:
        photo_id = user_photo
    print(f'{photo_id}')
    return photo_id


# ----- ИЗМЕНЕНИЕ ФОТО -----

# Загрузкого нового фото страницы


def update_user_photo(user_tg_id, photo_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users 
                    SET photo_id = %s 
                    WHERE user_tg_id = %s
                    """,
                    (photo_id, user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка добавления фото: {e}')
    finally:
        connection.close()

# Удаление фото страницы


def delete_user_photo(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE users 
                    SET photo_id = %s 
                    WHERE user_tg_id = %s
                    """,
                    (no_photo_id, user_tg_id)
                )

    except Exception as e:
        print(f'Ошибка добавления фото: {e}')
    finally:
        connection.close()
