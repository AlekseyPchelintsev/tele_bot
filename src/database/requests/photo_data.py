from config import no_photo_id
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
from src.database.models import get_db_connection

# Проверка наличия фото при регистрации


async def get_user_photo_id(bot, user_tg_id):

    get_user_photo = await bot(GetUserProfilePhotos(user_id=user_tg_id))

    if get_user_photo.photos:
        return get_user_photo.photos[0][-1].file_id
    else:
        return no_photo_id


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
