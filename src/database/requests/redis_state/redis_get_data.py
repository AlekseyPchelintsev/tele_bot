import redis
from src.database.requests.check_turn_off_or_ban import get_turn_off_users, get_users_in_ban


# Настройка соединения с Redis
redis_client = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)


# сохраняю в redis данные удаленных и забаненых
def save_users_to_redis():
    turn_off_users = get_turn_off_users()
    banned_users = get_users_in_ban()

    # Сохраняю удалившихся пользователей в Redis
    if turn_off_users:
        redis_client.sadd('turn_off_users', *turn_off_users)
        print(f'SAVE TO REDIS TURN OFF USERS: {turn_off_users}')

    # Сохраняю заблокированных пользователей в Redis
    if banned_users:
        redis_client.sadd('banned_users', *banned_users)
        print(f'SAVE TO REDIS BANNED USERS: {banned_users}')


# удаляю из redis вновь включенную анкету пользователя
def remove_turned_off_user_from_redis(user_tg_id):
    # Удаляю пользователя из множества отключенных анкет
    redis_client.srem('turn_off_users', user_tg_id)


# удаляю из redis разбненного пользователя
def remove_unbaned_user_from_redis(user_tg_id):
    # Удаляю пользователя из множества удалившихся пользователей
    redis_client.srem('banned_users', user_tg_id)
