from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.db.base.repo import BaseRepo
from bot.core.db.repository.proxy import ProxyRepo
from bot.core.db.repository.session import SessionRepo
from bot.core.db.repository.user import UserRepo


class Repo(BaseRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.session = SessionRepo(session)
        self.user = UserRepo(session)
        self.proxy = ProxyRepo(session)
