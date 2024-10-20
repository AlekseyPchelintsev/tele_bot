import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from psycopg2.extras import RealDictCursor
from src.database.requests.exclude_users import get_exclude_users_ids
from src.database.requests.render_users import render_users
from src.database.models import get_db_connection


# ПРОВЕРЯЕТ НАЛИЧИЕ ХОТЯ БЫ ОДНОГО ПОЛЬЗОВАТЕЛЯ
# В МОЕМ ГОРОДЕ ИЛИ В ГОРОДЕ ПО ЗАПРОСУ
# (возвращает True или False)
def check_users_in_city(user_tg_id, city_data, gender_data):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                if gender_data == 'all':

                    # получаю 1 пользователя любого пола
                    cursor.execute(
                        """
                        SELECT user_tg_id
                        FROM users
                        WHERE city = %s AND user_tg_id != %s
                        LIMIT 1
                        """, (city_data, user_tg_id)
                    )
                    check_user_id = cursor.fetchone()

                else:

                    # получаю 1 пользователя конкретного пола
                    cursor.execute(
                        """
                    SELECT user_tg_id
                    FROM users
                    WHERE city = %s AND gender = %s AND user_tg_id != %s
                    LIMIT 1
                    """, (city_data, gender_data, user_tg_id)
                    )
                    check_user_id = cursor.fetchone()

                if check_user_id:
                    return True
                else:
                    return False
    finally:
        connection.close()


# ----- ПОИСК ПОЛЬЗОВАТЕЛЕЙ ПО ХОББИ -----


# ВОЗВРАЩАЕТ список моих хобби пропущеных через nltk (стемминг) для поиска
def get_stemmed_hobbies_list(user_tg_id: int = None, hobby_name: str = None):

    # НАСТРОЙКА СТЕММЕРА
    # Настройка пути для nltk
    nltk.data.path.append('/Users/dude/dev/python/tele_bot/nltk_data')

    # Инициализация стеммера и списка стоп-слов
    language = 'russian'
    stemmer = SnowballStemmer(language)
    stop_words = set(stopwords.words(language))

    # Если передана строка hobby_name, выполняем стемминг для её слов и возвращаем результат
    if hobby_name:
        return [
            ' '.join(
                stemmer.stem(word.lower())  # Стемминг для каждого слова
                for word in hobby_name.split()  # Разбиваем строку на слова
                if word.lower() not in stop_words  # Убираем стоп-слова
            )
        ]

    # Если передан user_tg_id, выполняем поиск "моих" хобби в бд
    if user_tg_id is not None:
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

                    if not hobbies:

                        return False

                    else:

                        # Применяем стемминг к каждому слову в каждом хобби
                        stemmed_hobbies = [
                            ' '.join(
                                stemmer.stem(word.lower())
                                for word in hobby[0].split()
                                if word.lower() not in stop_words
                            )
                            for hobby in hobbies
                        ]

                        # Удаляем пустые строки, если они есть (на всякий случай)
                        return [hobby for hobby in stemmed_hobbies if hobby]

        finally:
            connection.close()


# ПРОВЕРЯЕТ НАЛИЧИЕ ХОТЯ БЫ ОДНОГО ПОЛЬЗОВАТЕЛЯ (ВОЗВРАЩАЕТ True False)
# с учетом запроса пола и города
def check_users_by_hobbies(my_user_tg_id, gender, city, hobbies):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # Базовый SQL-запрос с фильтрами и LIMIT 1
                base_query = """
                SELECT users.user_tg_id
                FROM users
                LEFT JOIN userhobbies ON users.user_tg_id = userhobbies.user_tg_id
                WHERE users.user_tg_id != %s
                """
                params = [my_user_tg_id]

                # Добавляем фильтр по полу, если значение не "all"
                if gender != "all":
                    base_query += " AND users.gender = %s"
                    params.append(gender)

                # Добавляем фильтр по городу, если значение не "all"
                if city != "all":
                    base_query += " AND users.city ILIKE %s"
                    params.append(f"%{city}%")

                # Первый запрос: подстрочный поиск по полным хобби
                if hobbies != ["all"]:
                    hobby_filters = " OR ".join(
                        ["userhobbies.hobby_name ILIKE %s"] * len(hobbies)
                    )
                    query_full_match = base_query + \
                        f" AND ({hobby_filters}) LIMIT 1"
                    params_full_match = params + \
                        [f"%{hobby}%" for hobby in hobbies]

                    # Выполняем первый запрос
                    cursor.execute(query_full_match, params_full_match)
                    if cursor.fetchone():  # Если найдено первое совпадение
                        return True

                # Второй запрос: поиск по словам, если первый не дал результата
                hobby_conditions = []
                for hobby in hobbies:
                    words = hobby.split()  # Разбиваем хобби на отдельные слова
                    word_filters = " OR ".join(
                        ["userhobbies.hobby_name ILIKE %s"] * len(words)
                    )
                    hobby_conditions.append(f"({word_filters})")
                    params.extend([f"%{word}%" for word in words])

                query_word_match = base_query + \
                    f" AND ({' OR '.join(hobby_conditions)}) LIMIT 1"

                # Выполняем второй запрос
                cursor.execute(query_word_match, params)
                result = cursor.fetchone()

                # Возвращаем True, если есть хотя бы 1 совпадение
                if result:
                    return True
                else:
                    return False

    finally:
        connection.close()


# НАХОДИТ ID ВСЕХ ПОЛЬЗОВАТЕЛЕЙ, ОБРАБАТЫВАЕТ IDs И ВОЗВРАЩАЕТ ОБРАБОТАННЫЕ ДАННЫЕ
def search_users(user_tg_id, gender, city, hobbies):
    # Получаем список пользователей для исключения
    exclude_users_ids = get_exclude_users_ids(user_tg_id)

    # Преобразуем хобби в список, если передано строкой
    if isinstance(hobbies, str):
        hobbies = [hobbies]

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                # Базовый запрос с исключением пользователей
                base_query = """
                SELECT users.user_tg_id
                FROM users
                LEFT JOIN userhobbies ON users.user_tg_id = userhobbies.user_tg_id
                WHERE users.user_tg_id != %s
                """
                params = [user_tg_id]

                # Добавляем фильтр на исключение пользователей
                if exclude_users_ids:
                    placeholders = ', '.join(['%s'] * len(exclude_users_ids))
                    base_query += (f" AND users.user_tg_id NOT IN "
                                   f"({placeholders})")
                    params.extend(exclude_users_ids)

                # Фильтр по полу
                if gender != "all":
                    base_query += " AND users.gender = %s"
                    params.append(gender)

                # Фильтр по городу
                if city != "all":
                    base_query += " AND users.city = %s"
                    params.append(city)

                # Если hobbies = ["all"], возвращаем без фильтра по хобби
                if hobbies == ["all"]:

                    cursor.execute(base_query, params)
                    users = cursor.fetchall()
                    return render_users([user[0] for user in users])

                # Первый запрос: построчный поиск по полным хобби
                hobby_filters = " OR ".join(
                    ["userhobbies.hobby_name ILIKE %s"] * len(hobbies))
                query_with_hobbies = f"{base_query} AND ({hobby_filters})"
                params_with_hobbies = params + \
                    [f"%{hobby}%" for hobby in hobbies]

                cursor.execute(query_with_hobbies, params_with_hobbies)
                users = cursor.fetchall()

                # Если найдено 5 и более пользователей, возвращаем результат
                if len(users) >= 5:
                    return render_users([user[0] for user in users])

                # Второй запрос: поиск по отдельным словам, если найдено менее 5 пользователей
                hobby_conditions = []
                params_word_match = params.copy()

                for hobby in hobbies:
                    words = hobby.split()  # Разбиваем хобби на слова
                    word_filters = " OR ".join(
                        ["userhobbies.hobby_name ILIKE %s"] * len(words))
                    hobby_conditions.append(f"({word_filters})")
                    params_word_match.extend([f"%{word}%" for word in words])

                query_word_match = f"{
                    base_query} AND ({' OR '.join(hobby_conditions)})"

                cursor.execute(query_word_match, params_word_match)
                users = cursor.fetchall()

                # Возвращаем список пользователей
                return render_users([user[0] for user in users])

    finally:
        connection.close()
