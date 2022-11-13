from sqlalchemy import select

from bot.core.db.models import User
from .base_repo import BaseRepo


class UserRepo(BaseRepo):
    async def add(self, id: int) -> None:
        user = User(id=id)
        await self.commit(user)

    async def get(self, id: int) -> User:
        stmt = select(User).where(User.id == id)
        return await self.session.scalar(stmt)
