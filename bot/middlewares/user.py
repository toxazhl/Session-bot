from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.core.db.repo import Repo


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from_user: User = data.get("event_from_user")
        repo: Repo = data["repo"]

        if from_user:
            user = await repo.get_user(id=from_user.id)
            data["user"] = user

        return await handler(event, data)
