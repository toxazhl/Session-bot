import asyncio
import logging
from datetime import datetime, timedelta
from secrets import token_urlsafe

from pyrogram.client import Client as PyroClient

from bot.core.session.exceptions import ClientNotFoundError
from bot.core.session.proxy import ProxyManager

logger = logging.getLogger(__name__)


class Client(PyroClient):
    def __init__(self, client_manager: "ClientManager", timeout: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
        self.client_manager = client_manager
        self.create_date = datetime.now()
        self.phone_code_hash = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.client_manager.terminate(self.name)
        except KeyError:
            pass

    async def send_code(self, phone_number: None | str = None):
        if phone_number:
            self.phone_number = phone_number

        if self.phone_number is None:
            raise ValueError("phone_number is None")

        sent_code = await super().send_code(self.phone_number)
        self.phone_code_hash = sent_code.phone_code_hash
        return sent_code

    async def sign_in(self, phone_code: str):
        if self.phone_code_hash is None:
            raise ValueError("phone_code_hash is None")

        if self.phone_number is None:
            raise ValueError("phone_number is None")

        return await super().sign_in(
            self.phone_number, self.phone_code_hash, phone_code
        )


class ClientManager:
    def __init__(self, proxy_manager: ProxyManager) -> None:
        self.proxy_manager = proxy_manager
        self.clients: dict[str, Client] = {}

    def new(
        self,
        api_id: int | str,
        api_hash: str,
        app_version: str = PyroClient.APP_VERSION,
        device_model: str = PyroClient.DEVICE_MODEL,
        system_version: str = PyroClient.SYSTEM_VERSION,
        lang_code: str = PyroClient.LANG_CODE,
        proxy: None | dict = None,
        session_string: None | str = None,
        phone_number: None | str = None,
        no_updates: None | bool = None,
        takeout: None | bool = None,
        name: None | str | int = None,
        timeout: int = 600,
    ) -> Client:
        if name is None:
            name = token_urlsafe(8)

        if proxy is None:
            proxy = self.proxy_manager.get_pyro()

        client = Client(
            client_manager=self,
            timeout=timeout,
            name=str(name),
            api_id=api_id,
            api_hash=api_hash,
            app_version=app_version,
            device_model=device_model,
            system_version=system_version,
            lang_code=lang_code,
            proxy=proxy,
            session_string=session_string,
            in_memory=True,
            phone_number=phone_number,
            no_updates=no_updates,
            takeout=takeout,
        )

        self.clients[str(name)] = client

        return client

    def get(self, name: str | int) -> Client:
        client = self.clients.get(str(name))
        if not client:
            raise ClientNotFoundError

        return client

    async def terminate(self, name: str | int) -> None:
        client = self.clients.pop(str(name))
        try:
            await client.stop()
        except ConnectionError:
            pass

    async def terminate_timeout(self) -> None:
        timeout_clients = [
            self.terminate(name)
            for name, client in self.clients.items()
            if client.create_date + timedelta(seconds=client.timeout) > datetime.now()
        ]

        await asyncio.gather(*timeout_clients)

        # logger.debug(f"Terminate client {name}")
        # try:
        #     await self.terminate(name)
        # except KeyError:
        #     pass
