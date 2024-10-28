from src.database.models import get_db_connection
from psycopg2.extras import RealDictCursor

'''
def render_users1(user_tg_ids):

    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return []

                # Получаем данные пользователей
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

                # Получаем хобби пользователей
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

                # Формируем список данных пользователей
                data = [(row['user_tg_id'],
                         row['name'],
                         row['photo_id'],
                         row['nickname'],
                         row['gender'],
                         row['age'],
                         row['city'])
                        for row in user_data]

                # Собираем хобби пользователей
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


def render_users2(user_tg_ids):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return []

                # Получаем данные пользователей
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

                # Получаем хобби пользователей
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

                # Собираем хобби пользователей
                hobbies = {}
                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobby_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobby_name)

                # Формируем данные пользователей
                data = []
                for row in user_data:
                    user_tg_id = row['user_tg_id']

                    # Получаем список хобби
                    hobbies_list = hobbies.get(user_tg_id, [])

                    # Получаем поле about_me для каждого пользователя
                    cursor.execute(
                        """
                        SELECT about_me 
                        FROM aboutme
                        WHERE user_tg_id = %s
                        """, (user_tg_id,)
                    )
                    user_about_me = cursor.fetchone()
                    about_me = user_about_me['about_me'] if user_about_me else '-'

                    # Собираем все данные в кортеж и добавляем в итоговый список
                    data.append((
                        row['user_tg_id'],
                        row['name'],
                        row['photo_id'],
                        row['nickname'],
                        row['gender'],
                        row['age'],
                        row['city'],
                        hobbies_list,
                        about_me
                    ))

                return data
    finally:
        connection.close()
'''

'''
def render_users3(user_tg_ids):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return []

                # Получаем данные пользователей с сохранением порядка
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
                    ORDER BY array_position(%s, user_tg_id)
                    """, (list(user_tg_ids), list(user_tg_ids))
                )
                user_data = cursor.fetchall()

                # Получаем хобби пользователей
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

                # получаю данные о роде деятельности
                cursor.execute(
                    """
                    SELECT 
                        work_or_study,
                        work_or_study_info
                    FROM workandstudy
                    WHERE user_tg_id = %s
                    """, (list(user_tg_ids),)
                )
                employment_data = cursor.fetchall()

                # Собираем хобби пользователей
                hobbies = {}
                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobby_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobby_name)

                # Формируем данные пользователей в нужном порядке
                data = []
                for row in user_data:
                    user_tg_id = row['user_tg_id']

                    # Получаем список хобби
                    hobbies_list = hobbies.get(user_tg_id, [])

                    # Получаем поле about_me для каждого пользователя
                    cursor.execute(
                        """
                        SELECT about_me 
                        FROM aboutme
                        WHERE user_tg_id = %s
                        """, (user_tg_id,)
                    )
                    user_about_me = cursor.fetchone()
                    about_me = user_about_me['about_me'] if user_about_me else '-'

                    # Собираем все данные в кортеж и добавляем в итоговый список
                    data.append((
                        row['user_tg_id'],
                        row['name'],
                        row['photo_id'],
                        row['nickname'],
                        row['gender'],
                        row['age'],
                        row['city'],
                        hobbies_list,
                        about_me
                    ))

                return data
    finally:
        connection.close()
'''


def render_users(user_tg_ids):
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if not user_tg_ids:
                    return []

                # Получаем данные пользователей с сохранением порядка
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
                    ORDER BY array_position(%s, user_tg_id)
                    """, (list(user_tg_ids), list(user_tg_ids))
                )
                user_data = cursor.fetchall()

                # Получаем хобби пользователей
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

                # Получаем данные о занятости пользователей
                cursor.execute(
                    """
                    SELECT 
                        user_tg_id,
                        work_or_study,
                        work_or_study_info
                    FROM workandstudy
                    WHERE user_tg_id = ANY(%s)
                    """, (list(user_tg_ids),)
                )
                employment_data = cursor.fetchall()

                # Обрабатываем хобби пользователей
                hobbies = {}
                for row in hobbies_data:
                    user_tg_id = row['user_tg_id']
                    hobby_name = row['hobby_name']
                    hobbies.setdefault(user_tg_id, []).append(hobby_name)

                # Обрабатываем данные о занятости пользователей
                employments = {}
                for row in employment_data:
                    user_tg_id = row['user_tg_id']
                    work_or_study = row['work_or_study']
                    work_or_study_info = row['work_or_study_info']
                    employments[user_tg_id] = (
                        work_or_study, work_or_study_info)

                # Формируем данные пользователей в нужном порядке
                data = []
                for row in user_data:
                    user_tg_id = row['user_tg_id']

                    # Получаем список хобби
                    hobbies_list = hobbies.get(user_tg_id, [])

                    # Получаем поле about_me для каждого пользователя
                    cursor.execute(
                        """
                        SELECT about_me 
                        FROM aboutme
                        WHERE user_tg_id = %s
                        """, (user_tg_id,)
                    )
                    user_about_me = cursor.fetchone()
                    about_me = user_about_me['about_me'] if user_about_me else '-'

                    # Получаем данные о занятости
                    employment_info = employments.get(user_tg_id, ('-', '-'))

                    # Собираем все данные в кортеж и добавляем в итоговый список
                    data.append((
                        row['user_tg_id'],
                        row['name'],
                        row['photo_id'],
                        row['nickname'],
                        row['gender'],
                        row['age'],
                        row['city'],
                        hobbies_list,
                        about_me,
                        employment_info  # Добавляем данные о занятости
                    ))

                return data
    finally:
        connection.close()
