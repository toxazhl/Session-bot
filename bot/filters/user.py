from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.core.db.models import User


class NewUserFilter(BaseFilter):
    async def __call__(self, message: Message, user: User) -> bool:
        return user is None
