from sqlalchemy import select

from bot.core.db.base.repo import BaseRepo
from bot.core.db.models import User


class UserRepo(BaseRepo):
    async def add(self, id: int) -> None:
        user = User(id=id)
        await self.commit(user)

    async def get(self, id: int) -> User:
        stmt = select(User).where(User.id == id)
        return await self._scalar(stmt)
