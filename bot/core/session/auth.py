import logging
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Type

from opentele.api import APIData
from pyrogram.client import Client

from bot.core.session.exceptions import ClientNotFoundError
from bot.core.session.proxy import ProxyManager

logger = logging.getLogger(__name__)


class DTClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_date = datetime.now()


class AuthManager:
    def __init__(self, proxy_manager: ProxyManager, timeout: int = 600) -> None:
        self.proxy_manager = proxy_manager
        self.timeout = timeout
        self.clients: dict[int, DTClient] = {}

    async def create(self, user_id: int, api: Type[APIData], **kwargs) -> DTClient:
        client = DTClient(
            name=token_urlsafe(8),
            api_id=api.api_id,
            api_hash=api.api_hash,
            app_version=api.app_version,
            device_model=api.device_model,
            system_version=api.system_version,
            lang_code=api.lang_code,
            proxy=self.proxy_manager.get_pyro(),
            in_memory=True,
            **kwargs,
        )
        await client.connect()
        self.clients[user_id] = client
        return client

    def get(self, user_id: int) -> DTClient:
        client = self.clients.get(user_id)
        if not client:
            raise ClientNotFoundError

        return client

    async def close(self, user_id: int) -> None:
        client = self.clients.pop(user_id)
        await client.disconnect()

    async def timeout_close(self) -> None:
        for user_id, client in self.clients.items():
            if client.create_date + timedelta(seconds=self.timeout) > datetime.now():
                self.clients.pop(user_id)
                await client.stop()
                logger.debug(f"Terminated client from user {user_id}")
