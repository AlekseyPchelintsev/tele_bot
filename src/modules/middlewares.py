from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User, BotCommand, BotCommandScopeChat, Message
from aiogram.dispatcher.flags import get_flag
from typing import Any, Awaitable, Callable, Dict
from src.database.requests.redis_state.redis_get_data import redis_client
from config import ADMIN_IDs
from src.modules.notifications import attention_message


# мидлварь для фильтра отключившихся пользователей
class TurnOffUsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Получаю данные о пользователях из Redis (список удалённых)
        turn_off_users = {int(user_tg_id)
                          for user_tg_id in redis_client.smembers('turn_off_users')}

        # Получаю флаг allow_deleted для текущего обработчика, если он установлен
        allow_turned_off_users = get_flag(
            data.get("handler"), "allow_turned_off_users")

        # Проверяю, есть ли текущий пользователь в списке удалённых
        user: User = data.get('event_from_user')
        if user and user.id in turn_off_users:

            if not allow_turned_off_users:
                # Если пользователь в списке удалённых и флаг не установлен:
                # блокирую доступ
                return

            else:
                # Если пользователь в списке удалённых, но флаг установлен:
                # пропускаю обработчик
                return await handler(event, data)

        # Если пользователь не в списке удалённых:
        # проверяю отправку команды для включения анкеты
        # и в зависимости от этого - вывожу уведомление и
        # пропускаю в любой обработчик

        turn_on_commands = ['🔌 Включить профиль',
                            'Включить профиль', 'включить профиль']

        if hasattr(event, 'text') and event.text in turn_on_commands:
            await event.delete()
            await attention_message(event, '⚠️ Если вы хотите внести изменения, перейдите '
                                    'в раздел <b>"редактировать профиль"</b>', 3)
            return await handler(event, data)

        else:

            return await handler(event, data)


# мидлварь для забаненых пользователей
class BannedUsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Получаю данные о пользователях из Redis (список удалённых)
        check_banned_users = {int(user_tg_id)
                              for user_tg_id in redis_client.smembers('banned_users')}

        # Проверяю, забанен ли текущий пользователь
        user: User = data.get('event_from_user')
        if user and user.id in check_banned_users:

            # если забанен - игнорирую любые апдейты от него
            return

        # Если пользователь не забанен:
        # пропускаю в любой обработчик
        return await handler(event, data)

# мидлварь для админа


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        check_admin = get_flag(data.get("handler"), "check_admin")

        # Проверяю, забанен ли текущий пользователь
        user: User = data.get('event_from_user')
        if user and user.id in ADMIN_IDs and check_admin:

            return await handler(event, data)

        if check_admin:

            return

        return await handler(event, data)


# установка команд в меню (синяя кнопка)
async def set_admin_commands_menu(bot: Bot, ADMIN_IDs):

    # Дополнительные команды для администратора
    admin_commands = [
        BotCommand(command="start", description="Общий старт"),
        BotCommand(command="startadmin", description="Администрирование"),
        BotCommand(command="test", description="Тестирование функций")
    ]

    for admin_id in ADMIN_IDs:
        await bot.set_my_commands(commands=admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
