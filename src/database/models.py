
from psycopg2 import OperationalError
import psycopg2
from config import user, password, database, host


def create_tables():
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_tg_id bigint PRIMARY KEY,
                        name varchar(30),
                        photo_id text,
                        nickname text,
                        gender varchar(10),
                        age int,
                        birth_date varchar(10),
                        city varchar(30)
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS hobbies (
                        id SERIAL PRIMARY KEY,
                        hobby_name varchar(50) 
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS userhobbies (
                        hobby_id int,
                        hobby_name varchar(50),
                        user_tg_id bigint,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id) ON DELETE CASCADE
                    )
                    """
                )

    finally:
        connection.close()


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
