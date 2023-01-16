import logging
from typing import Any

from sqlalchemy.orm import sessionmaker

from bot.core.db.models import Proxy
from bot.core.db.repo import Repo

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, db_pool: sessionmaker):
        self.db_pool = db_pool
        self.proxies: list[Proxy] = []
        self.n = 0

    async def update(self):
        async with self.db_pool() as session:
            self.proxies = await Repo(session).get_all_proxies()
            # logger.debug(f"Updated {len(self.proxies)} proxies")

    def get(self) -> None | Proxy:
        if self.proxies:
            self.n += 1
            if self.n >= len(self.proxies):
                self.n = 0
            return self.proxies[self.n]

    def get_pyro(self) -> None | dict[str, Any]:
        proxy = self.get()
        if proxy:
            return proxy.pyro_format()

    def get_telethon(self) -> None | tuple:
        proxy = self.get()
        if proxy:
            return proxy.telethon_format()
