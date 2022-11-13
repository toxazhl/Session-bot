from sqlalchemy.ext.asyncio import AsyncSession

from .user import UserRepo
from .base_repo import BaseRepo


class Repo(BaseRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.user = UserRepo(session)
