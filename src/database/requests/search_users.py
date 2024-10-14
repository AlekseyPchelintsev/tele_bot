import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from psycopg2.extras import RealDictCursor
from src.database.models import get_db_connection

# изменение пути nltk_data для подключения списка "стоп" слов
nltk.data.path.append('/Users/dude/dev/python/tele_bot/nltk_data')

# Инициализация стеммера и списка стоп-слов
language = 'russian'

# Инициализация стеммера для русского языка
stemmer = SnowballStemmer(language)

# инициализация списка "стоп" слов
stop_words = set(stopwords.words(language))

# ----- ПОИСК ПО ХОББИ -----

# список моих хобби готовых для поиска


def get_stemmed_self_hobbies(user_tg_id):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT hobby_name
                    FROM userhobbies
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

                hobbies = cursor.fetchall()

                # Применяем стемминг к каждому хобби и фильтруем стоп-слова
                stemmed_hobbies = [
                    stemmer.stem(hobby[0].lower())
                    for hobby in hobbies
                    if hobby[0].lower() not in stop_words
                ]

                return stemmed_hobbies

    finally:
        connection.close()

# проверка наличия хотя бы одного пользователя по моим хобби в таблице userhobbies


def check_users_by_self_hobby(user_tg_id):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                # Получаем хобби пользователя
                cursor.execute(
                    """
                    SELECT hobby_name
                    FROM userhobbies
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

                hobbies = cursor.fetchall()

                # Если у пользователя нет хобби, возвращаем False
                if not hobbies:
                    return False

                # стемминг и фильтрация стоп-слов
                processed_hobbies = [
                    stemmer.stem(hobby[0].lower())
                    for hobby in hobbies
                    if hobby[0].lower() not in stop_words
                ]

                # запрос с использованием LIKE
                like_conditions = " OR ".join(
                    ["hobby_name LIKE %s" for _ in processed_hobbies])
                like_values = [f"%{hobby}%" for hobby in processed_hobbies]

                cursor.execute(
                    f"""
                    SELECT user_tg_id
                    FROM userhobbies
                    WHERE ({like_conditions}) AND user_tg_id != %s
                    LIMIT 1
                    """, (*like_values, user_tg_id)
                )

                user_id = cursor.fetchone()

                if user_id:
                    return True
                else:
                    return False

    finally:
        connection.close()

# функция выводит всех пользователей хотя бы
# по 1 совпадению с хобби (в том числе и многословным)


def check_users_by_hobby(hobby_name, user_tg_id):

    connection = get_db_connection()

    # print(f'ФАЙЛ SEARCH_USERS: {hobby_name}')

    try:
        with connection:
            with connection.cursor() as cursor:

                # формирование запроса
                like_conditions = " OR ".join(
                    [f"hobby_name LIKE %s" for _ in hobby_name])

                # передает каждое слово из запроса (%word% не строгое соответствие)
                params = [f'%{word}%' for word in hobby_name]

                # тело SQL-запроса
                sql_query = f"""
                SELECT DISTINCT user_tg_id
                FROM userhobbies
                WHERE ({like_conditions}) AND user_tg_id != %s
                """

                # запрос к бд
                cursor.execute(sql_query, params + [user_tg_id])

                # плучаю список id
                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()

# функция выводит всех пользователей хотя бы
# по 1 совпадению с списком хобби (в том числе и многословных)


def get_users_by_self_hobby(hobby_name, user_tg_id):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                # Формирование условий LIKE для каждого слова в каждом хобби
                like_conditions = []
                params = []

                for hobby in hobby_name:
                    # Разбиваем хобби на слова
                    words = hobby.split()
                    # Формируем условия LIKE для каждого слова
                    conditions = " AND ".join(
                        [f"hobby_name LIKE %s" for _ in words])
                    like_conditions.append(f"({conditions})")
                    # Добавляем параметры для каждого слова
                    params.extend([f'%{word}%' for word in words])

                    # Выводим текущее состояние like_conditions
                    print(f"Текущие условия для хобби '{hobby}': {conditions}")
                    print(f"Текущие like_conditions: {like_conditions}")

                # Объединяем все условия
                final_like_conditions = " OR ".join(like_conditions)

                # Выводим финальные условия
                print(f"Финальные условия: {final_like_conditions}")

                # Тело SQL-запроса
                sql_query = f"""
                SELECT DISTINCT user_tg_id
                FROM userhobbies
                WHERE ({final_like_conditions}) AND user_tg_id != %s
                """

                # Запрос к БД
                cursor.execute(sql_query, params + [user_tg_id])

                # Получаем список id
                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()


# Выборка пользователей по хобби из таблицы userhobbies


def get_users_by_hobby(hobby, user_tg_id, gender_data, exclude_ids=None):
    connection = get_db_connection()

    user_tg_ids_hobby = check_users_by_hobby(hobby, user_tg_id)
    user_tg_ids_gender = check_users_by_gender(user_tg_id, gender_data)

    try:
        # Извлекаю ID пользователей из кортежей
        user_tg_ids_hobby = {uid for (uid,) in user_tg_ids_hobby}
        user_tg_ids_gender = {uid for (uid,) in user_tg_ids_gender}
        # Нахожу пересечение
        user_tg_ids = user_tg_ids_hobby & user_tg_ids_gender
    except:
        return

    # Исключаю указанные ID, если они есть
    if exclude_ids is not None:
        user_tg_ids -= set(exclude_ids)

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return
                else:
                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id, 
                            name, 
                            photo_id, 
                            nickname, 
                            gender, 
                            age,
                            city
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (list(user_tg_ids),)
                    )
                    user_data = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id,
                            hobby_name
                        FROM userhobbies
                        WHERE user_tg_id = ANY(%s)   
                        """, (list(user_tg_ids),)
                    )
                    hobbies_data = cursor.fetchall()

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['nickname'],
                             row['gender'],
                             row['age'],
                             row['city'])
                            for row in user_data]

                hobbies = {}

                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobby_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobby_name)

                # Добавляем список хобби к данным пользователей
                for i in range(len(data)):
                    user_tg_id = data[i][0]  # Извлекаем user_tg_id
                    hobbies_list = hobbies.get(
                        user_tg_id)  # Получаем список хобби
                    data[i] = (*data[i], hobbies_list)

                return data
    finally:
        connection.close()

# ----- ПОИСК ПО ГОРОДУ -----

# поиск в моем городе


def check_users_self_city(user_tg_id, gender_data):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT city
                    FROM users
                    WHERE user_tg_id = %s
                    """, (user_tg_id,)
                )

                user_city = cursor.fetchone()
                user_city_row = user_city[0]

                if gender_data == 'all':

                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE city = %s AND user_tg_id != %s
                        """, (user_city_row, user_tg_id)
                    )
                    user_tg_ids = cursor.fetchone()

                else:

                    cursor.execute(
                        """
                    SELECT user_tg_id
                    FROM users
                    WHERE city = %s AND gender = %s AND user_tg_id != %s
                    """, (user_city_row, gender_data, user_tg_id)
                    )
                    user_tg_ids = cursor.fetchone()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()

# поиск по названию города


def check_users_by_city(user_tg_id, city_name, gender_data):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT user_tg_id
                    FROM users
                    WHERE city = %s AND gender = %s AND user_tg_id != %s
                    """, (city_name, gender_data, user_tg_id)
                )

                user_id = cursor.fetchone()

                if user_id:
                    return True
                else:
                    return False

    finally:
        connection.close()


# ----- ПОИСК ПО ПОЛУ -----

# Проверка наличия пользователей определенного пола


def check_users_by_gender(user_tg_id, gender_data):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                if gender_data == 'all':
                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE user_tg_id != %s
                        """, (user_tg_id,)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE gender = %s AND user_tg_id != %s
                        """, (gender_data, user_tg_id)
                    )

                user_tg_ids = cursor.fetchall()

                if not user_tg_ids:
                    return
                return user_tg_ids
    finally:
        connection.close()


def get_users_by_gender(user_tg_id, gender_data):
    connection = get_db_connection()
    user_tg_ids = check_users_by_gender(user_tg_id, gender_data)

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return
                else:
                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id, 
                            name, 
                            photo_id, 
                            nickname, 
                            gender, 
                            age,
                            city
                        FROM users 
                        WHERE user_tg_id = ANY(%s)
                        """, (user_tg_ids,)
                    )
                    user_data = cursor.fetchall()

                    cursor.execute(
                        """
                        SELECT 
                            user_tg_id,
                            hobby_name
                        FROM userhobbies
                        WHERE user_tg_id = ANY(%s)   
                        """, (user_tg_ids,)
                    )
                    hobbies_data = cursor.fetchall()

                    data = [(row['user_tg_id'],
                             row['name'],
                             row['photo_id'],
                             row['nickname'],
                             row['gender'],
                             row['age'],
                             row['city'])
                            for row in user_data]

                hobbies = {}

                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobbie_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobbie_name)

                # Добавляем список хобби к данным пользователей
                for i in range(len(data)):
                    user_tg_id = data[i][0]  # Извлекаем user_tg_id
                    hobbies_list = hobbies.get(
                        user_tg_id)  # Получаем список хобби
                    data[i] = (*data[i], hobbies_list)

                return data
    finally:
        connection.close()
