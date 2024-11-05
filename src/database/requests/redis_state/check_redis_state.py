import asyncio
import redis
from src.database.requests.redis_state.redis_get_data import redis_client, save_users_to_redis


# Последнее известное время загрузки Redis из RDB
last_redis_load_time = 0


async def check_redis_state():
    global last_redis_load_time
    try:
        # Получаю текущее время последнего сохранения RDB файла
        current_load_time = int(
            redis_client.info().get('rdb_last_save_time', 0))

        # Если время загрузки изменилось, значит, сервер был перезагружен
        if current_load_time != last_redis_load_time:
            print("Redis был перезагружен или данные отсутствуют. Обновляю данные из БД.")
            save_users_to_redis()

            # Обновляю время последнего сохранения
            last_redis_load_time = current_load_time
        else:
            print('Redis запущен и данные на месте')
    except redis.ConnectionError:
        print("Не удалось подключиться к Redis.")


# Функция для фоновой проверки состояния Redis
async def schedule_check():
    while True:
        await check_redis_state()
        await asyncio.sleep(300)


# Функция для запуска фонового процесса с обработчиком завершения
async def start_background_tasks(dp):

    # Запуск фоновой задачи для проверки состояния Redis
    task = asyncio.create_task(schedule_check())

    async def shutdown_background_tasks():
        print("Завершаю фоновую задачу проверки состояния Redis...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("Фоновая задача завершена.")

    # Регистрируем завершение фоновой задачи при завершении бота
    dp.shutdown.register(shutdown_background_tasks)
