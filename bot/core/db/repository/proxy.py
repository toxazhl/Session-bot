from sqlalchemy import select

from bot.core.db.models import Proxy
from .base_repo import BaseRepo


class ProxyRepo(BaseRepo):
    async def get_best(self) -> Proxy | None:
        stmt = select(Proxy).order_by(Proxy.uses)
        proxy = await self.scalar(stmt)

        if proxy:
            proxy.uses += 1
            await self.commit(proxy)
            return proxy
