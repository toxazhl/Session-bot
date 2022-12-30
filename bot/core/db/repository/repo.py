from sqlalchemy.ext.asyncio import AsyncSession

from .session import SessionRepo
from .user import UserRepo
from .proxy import ProxyRepo
from .base_repo import BaseRepo


class Repo(BaseRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.session = SessionRepo(session)
        self.user = UserRepo(session)
        self.proxy = ProxyRepo(session)
