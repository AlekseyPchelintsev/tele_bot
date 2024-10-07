from psycopg2.extras import RealDictCursor
from src.database.models import get_db_connection


# ----- ИНТЕРЕСЫ -----

# Проверка существования хобби при добавлении нового


def check_hobby(user_tg_id, hobby):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:

                cursor.execute(
                    """
                    SELECT 
                        id,
                        hobby_name
                    FROM hobbies
                    WHERE hobby_name = %s
                    """,
                    (hobby,)
                )

                exist_hobby = cursor.fetchone()

                if exist_hobby:

                    hobby_id = exist_hobby['id']

                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id,
                            hobby_id
                        FROM userhobbies
                        WHERE 
                            user_tg_id = %s AND
                            hobby_id = %s
                        """,
                        (user_tg_id, hobby_id)
                    )

                    match = cursor.fetchone()

                    if match:
                        return False

                    else:
                        add_hobbie_to_user(user_tg_id, hobby_id, hobby)
                        return True
                else:

                    new_hobby_id = add_new_hobby(hobby)
                    add_hobbie_to_user(user_tg_id, new_hobby_id, hobby)
                    return True

    finally:
        connection.close()


# Добавление хобби в общую db Hobbies


def add_new_hobby(hobby):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO hobbies (hobby_name)
                    VALUES (%s)
                    """,
                    (hobby,)
                )

                cursor.execute(
                    """
                    SELECT id
                    FROM hobbies
                    WHERE hobby_name = %s
                    """,
                    (hobby,)
                )
                hobby_id = cursor.fetchone()

                return hobby_id
    finally:
        connection.close()

# Добавление хобби для конкретного пользователя в db UserHobbies


def add_hobbie_to_user(user_tg_id, new_hobby_id, hobbie):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO userhobbies (user_tg_id, 
                                            hobby_id, 
                                            hobby_name)
                    VALUES (%s, %s, %s)
                    """,
                    (user_tg_id, new_hobby_id, hobbie)
                )
    finally:
        connection.close()


# Удаление хобби у пользователя из db UserHobbies

def delete_hobby(user_tg_id, hobby):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        user_tg_id,
                        hobby_name
                    FROM userhobbies
                    WHERE
                        user_tg_id = %s AND
                        hobby_name = %s
                    """,
                    (user_tg_id, hobby)
                )
                hobby_to_delete = cursor.fetchone()

                if hobby_to_delete:
                    # Удаляем хобби для данного пользователя
                    cursor.execute(
                        """
                        DELETE FROM userhobbies
                        WHERE
                            user_tg_id = %s AND
                            hobby_name = %s
                        """,
                        (user_tg_id, hobby)
                    )
                    return True  # Успешно удалено
                else:
                    return False  # Хобби не найдено
    finally:
        connection.close()
