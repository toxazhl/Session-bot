import logging

from sqlalchemy.orm import sessionmaker

from bot.core.db import Repo
from bot.core.db.models import Proxy

logger = logging.getLogger()


class ProxyManager:
    def __init__(self, db_pool: sessionmaker):
        self.db_pool = db_pool
        self.proxies: list[Proxy] = []
        self.n = 0

    async def update(self):
        async with self.db_pool() as session:
            self.proxies = await Repo(session).proxy.get_all()
            logger.debug(f"Updated {len(self.proxies)} proxies")

    @property
    def get(self):
        if self.proxies:
            self.n += 1
            if self.n >= len(self.proxies):
                self.n = 0
            return self.proxies[self.n]
