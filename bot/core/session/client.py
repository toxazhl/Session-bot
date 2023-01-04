import asyncio
import logging
from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Type

from telethon import TelegramClient
from telethon.network import Connection, ConnectionTcpFull
from telethon.sessions import StringSession

from bot.core.session.exceptions import ClientAlredyExistError, ClientNotFoundError
from bot.core.session.proxy import ProxyManager

logger = logging.getLogger(__name__)


class Client(TelegramClient):
    def __init__(
        self,
        name: str | int,
        client_manager: "ClientManager",
        client_timeout: int,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.client_timeout = client_timeout
        self.client_manager = client_manager
        self.create_date = datetime.now()
        self.phone = None

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.client_manager.terminate(self.name)
        except KeyError:
            pass

    async def send_code(self, phone: str):
        self.phone = phone

        return await self.send_code_request(self.phone)

    async def sign_in(self, phone_code: None | str = None, password: None | str = None):
        return await super().sign_in(self.phone, code=phone_code, password=password)


class ClientManager:
    def __init__(self, proxy_manager: ProxyManager) -> None:
        self.proxy_manager = proxy_manager
        self.clients: dict[str | int, Client] = {}

    def new(
        self,
        api_id: int,
        api_hash: str,
        *,
        device_model: str,
        system_version: str,
        app_version: str,
        lang_code: str,
        system_lang_code: str,
        name: None | str | int = None,
        client_timeout: int = 600,
        session: None | str = None,
        proxy: None | tuple | dict = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        retry_delay: int = 1,
        flood_sleep_threshold: int = 60,
        auto_reconnect: bool = False,
        connection: Type[Connection] = ConnectionTcpFull,
        use_ipv6: bool = False,
        local_addr: None | str | tuple = None,
        sequential_updates: bool = False,
        raise_last_call_error: bool = False,
        receive_updates: bool = True,
        catch_up: bool = False,
    ) -> Client:
        if name is None:
            name = token_urlsafe(8)

        if proxy is None:
            proxy = self.proxy_manager.get_telethon()

        if isinstance(session, str):
            session = StringSession(session)

        if self.clients.get(name):
            raise ClientAlredyExistError()

        logger.debug(f"Creating client {name}")

        client = Client(
            name=name,
            client_manager=self,
            client_timeout=client_timeout,
            session=session,
            api_id=api_id,
            api_hash=api_hash,
            connection=connection,
            use_ipv6=use_ipv6,
            proxy=proxy,
            local_addr=local_addr,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            flood_sleep_threshold=flood_sleep_threshold,
            raise_last_call_error=raise_last_call_error,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
            base_logger=None,
            receive_updates=receive_updates,
            catch_up=catch_up,
        )
        self.clients[name] = client

        return client

    def get(self, name: str | int) -> Client:
        client = self.clients.get(name)
        if not client:
            raise ClientNotFoundError

        return client

    async def terminate(self, name: str | int, timeout: bool = False) -> None:
        client = self.clients[name]
        logger.debug(f"Terminating client={name}, timeout={timeout}")
        del self.clients[name]
        await client.disconnect()

    async def terminate_timeout(self) -> None:
        timeout_clients = [
            self.terminate(name, timeout=True)
            for name, client in self.clients.items()
            if client.create_date + timedelta(seconds=client.client_timeout)
            < datetime.now()
        ]

        await asyncio.gather(*timeout_clients)
