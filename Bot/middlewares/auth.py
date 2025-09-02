# Базовый класс для всех мидлвар
from aiogram import BaseMiddleware
# Сообщения, callback-кнопки
from aiogram.types import TelegramObject, Message, CallbackQuery

# Мой метод проверки доступа
from databases.db import get_user

from typing import Callable, Awaitable, Any, Dict


class AuthMiddleware(BaseMiddleware):
    """
    Мидлварь, вызывается каждый собтыие (сообщение, callback-кнопки и т.д).
    Получает пользователя и проверяет доступ, через get_user(...).
    Результат кладёт в data['is_allowed'].

    Всё, что полежно в data, можно принимать как аргументы хенделров (обработчиков) по имени:
    def start(message: Message, is_allowed: bool)
    """

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,  # событие (Message, CallbackQuery и т.д.)
                       data: Dict[str, Any],  # "контекст" — словарь, который увидят хэндлеры
                       ) -> Any:
        # По умолчанию доступа нет
        is_allowed = False

        # Ищем события, у которых есть from_user
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if user:
            tg_id = user.id
            nickname = user.username

            try:
                is_allowed = await get_user(nickname=nickname, tg_id=tg_id)
            except Exception:
                is_allowed = False

        # Убираю флаг в контекст
        data["is_allowed"] = is_allowed

        # Передаю управление следующему обработчику
        return await handler(event, data)
