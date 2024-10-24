from src.database.models import get_db_connection


# Добавление реакции в бд и проверка наличия ответной реакции
def add_to_favorites(user_tg_id_1, user_tg_id_2):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO favoriteusers (user_tg_id_1, user_tg_id_2)
                        VALUES (%s, %s)
                        ON CONFLICT (user_tg_id_1, user_tg_id_2) DO NOTHING;
                    """, (user_tg_id_1, user_tg_id_2))
    finally:
        connection.close()
