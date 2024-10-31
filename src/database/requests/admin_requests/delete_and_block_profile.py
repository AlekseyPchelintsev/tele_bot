from src.database.models import get_db_connection

# удаление пользователя из users и добавление в banlist


def delete_and_ban_user(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # добавляю пользователя в бан
                cursor.execute(
                    """
                        INSERT INTO banlist (user_tg_id) 
                        VALUES (%s)
                    """, (user_tg_id,)
                )

                # удаляю учетку забаненого пользователя
                cursor.execute(
                    """
                        DELETE FROM users 
                        WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

    except Exception as e:
        print(f'Ошибка бана и удаления анкеты: {e}')

    finally:
        connection.close()


# проверка наличия записи в banlist
def check_user_in_ban(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                        SELECT 1 FROM banlist 
                        WHERE user_tg_id = %s 
                        LIMIT 1;
                    """, (user_tg_id,)
                )

                data_check = cursor.fetchone()

                return data_check is not None

    except Exception as e:
        print(f'Ошибка проверки бан лисита: {e}')

    finally:
        connection.close()
