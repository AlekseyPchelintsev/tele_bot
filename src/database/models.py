
from psycopg2 import OperationalError
import psycopg2
from config import user, password, database, host


def create_tables():
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # основная таблица пользователей
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_tg_id BIGINT PRIMARY KEY NOT NULL,
                        name VARCHAR(30),
                        photo_id TEXT,
                        nickname TEXT,
                        gender VARCHAR(10),
                        age INT,
                        birth_date VARCHAR(10),
                        city VARCHAR(30),
                        date_time TIMESTAMP NOT NULL,
                        last_active TIMESTAMP
                    )
                    """
                )

                # таблица увлечений с id
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS hobbies (
                        id SERIAL PRIMARY KEY,
                        hobby_name VARCHAR(50) 
                    )
                    """
                )

                # увлечения пользователей
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS userhobbies (
                        id SERIAL PRIMARY KEY,
                        hobby_id INT,
                        hobby_name VARCHAR(50),
                        user_tg_id BIGINT,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE
                    )
                    """
                )

                # реакции пользователей (еще не взаименые)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS userreactions (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT NOT NULL,
                        like_tg_id BIGINT NOT NULL,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        FOREIGN KEY (like_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        UNIQUE (user_tg_id, like_tg_id)
                    )
                    """
                )

                # мои контакты
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS matchreactions (
                        id SERIAL PRIMARY KEY,
                        user_tg_id_1 BIGINT NOT NULL,
                        user_tg_id_2 BIGINT NOT NULL,
                        FOREIGN KEY (user_tg_id_1) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_tg_id_2) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        UNIQUE (user_tg_id_1, user_tg_id_2)
                    )
                    """
                )

                # раздел "Избранное"
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS favoriteusers (
                        id SERIAL PRIMARY KEY,
                        user_tg_id_1 BIGINT NOT NULL,
                        user_tg_id_2 BIGINT NOT NULL,
                        FOREIGN KEY (user_tg_id_1) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_tg_id_2) REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        UNIQUE (user_tg_id_1, user_tg_id_2)
                        )
                    """
                )

                # скрытые пользователи
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ignoreusers (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT NOT NULL,
                        ignore_user_id BIGINT NOT NULL,
                        UNIQUE (user_tg_id, ignore_user_id)
                    )
                    """
                )

                # раздел "О себе"
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS aboutme (
                    user_tg_id BIGINT NOT NULL PRIMARY KEY,
                    about_me TEXT,
                    UNIQUE (user_tg_id),
                    FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE
                    );
                    """
                )

                # сведения о работе/учебе
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workandstudy (
                    user_tg_id BIGINT NOT NULL PRIMARY KEY,
                    work_or_study TEXT,
                    work_or_study_info TEXT,
                    UNIQUE (user_tg_id),
                    FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE
                    );
                    """
                )

                # сбор неверных вводов даты рождения
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS birthdateerror (
                    id SERIAL PRIMARY KEY,
                    user_tg_id BIGINT NOT NULL,
                    wrong_birth_date TEXT
                    );
                    """
                )

                # список забаненых id
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS banlist (
                    user_tg_id BIGINT NOT NULL PRIMARY KEY,
                    UNIQUE (user_tg_id)
                    );
                    """
                )

    finally:
        connection.close()


# подключение к бд
def get_db_connection():
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            database=database,
            host=host
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
