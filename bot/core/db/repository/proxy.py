from sqlalchemy import select

from bot.core.db.base.repo import BaseRepo
from bot.core.db.models import Proxy


class ProxyRepo(BaseRepo):
    async def get_all(self) -> list[Proxy]:
        stmt = select(Proxy)
        return await self.scalars_all(stmt)
