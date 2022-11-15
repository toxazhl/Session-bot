from typing import TYPE_CHECKING

from opentele.api import API

from .pyro.session import PyroSession
from .tele.session import TeleSession
from .tdata.tdata_session import TDataSession

if TYPE_CHECKING:
    from pathlib import Path
    from uuid import UUID
    from typing import Type
    from bot.core.db import Repo
    from opentele.api import APIData


class SessionManager:
    def __init__(
        self,
        dc_id: int,
        auth_key: bytes,
        server_address: str,
        port: int,
        api_id: None | int = None,
        user_id: None | int = None,
        is_bot: bool = False,
        test_mode: bool = False,
        valid: None | bool = None,
        api: "Type[APIData]" = API.TelegramDesktop,
    ):
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.server_address = server_address
        self.port = port
        self.api_id = api_id
        self.user_id = user_id
        self.is_bot = is_bot
        self.test_mode = test_mode
        self.api: APIData = api.copy()
        self.valid = valid
        self.user = None

    async def __aenter__(self):
        self.client = self.telethon_client()
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()

    @property
    def auth_key_hex(self) -> str:
        return self.auth_key.hex()

    @classmethod
    async def from_database(cls, session_id: "UUID", repo: "Repo"):
        session = await repo.session.get(session_id)
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            server_address=session.server_address,
            port=session.port,
            api_id=session.api_id,
            user_id=session.telegram_id,
            is_bot=session.is_bot,
            test_mode=session.test_mode,
            valid=session.valid,
        )

    @classmethod
    def from_telethon_session(
        cls, session: TeleSession, api=API.TelegramDesktop
    ):
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            port=session.port,
            server_address=session.server_address,
            api=api
        )

    @classmethod
    async def from_telethon_file(cls, file: "Path", api=API.TelegramDesktop):
        session = await TeleSession.from_file(file)
        return cls.from_telethon_session(session, api=api)

    @classmethod
    def from_telethon_string(cls, string: str, api=API.TelegramDesktop):
        session = TeleSession.from_string(string)
        return cls.from_telethon_session(session, api=api)

    @classmethod
    def from_pyrogram_session(
        cls, session: PyroSession, api=API.TelegramDesktop
    ):
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            port=session.port,
            server_address=session.server_address,
            api=api,
            api_id=session.api_id,
            is_bot=session.is_bot,
            test_mode=session.test_mode,
            user_id=session.user_id,
        )

    @classmethod
    async def from_pyrogram_file(cls, file: "Path", api=API.TelegramDesktop):
        session = await PyroSession.from_file(file)
        return cls.from_pyrogram_session(session, api=api)

    @classmethod
    def from_pyrogram_string(cls, string: str, api=API.TelegramDesktop):
        session = PyroSession.from_string(string)
        return cls.from_pyrogram_session(session, api=api)

    @classmethod
    def from_tdata_folder(cls, folder: "Path"):
        session = TDataSession.from_tdata(folder)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            port=session.port,
            server_address=session.server_address,
            api=session.api
        )

    @property
    def pyrogram_session(self) -> PyroSession:
        return PyroSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            user_id=self.user_id,
            api_id=self.api_id,
            is_bot=self.is_bot,
            test_mode=self.test_mode,
        )

    @property
    def telethon_session(self) -> TeleSession:
        return TeleSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            server_address=self.server_address,
            port=self.port,
        )

    @property
    def tdata_session(self) -> TDataSession:
        return TDataSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            api=self.api,
            user_id=self.user_id,
        )

    async def validate(self) -> bool:
        user = await self.get_user()
        self.valid = bool(user)
        return self.valid

    async def get_user_id(self):
        if self.user_id:
            return self.user_id

        user = await self.get_user()

        if user is None:
            raise ValueError("Invalid session")

        self.user_id = user.id
        return self.user.id

    async def get_user(self):
        async with self as client:
            self.user = await client.get_me()
        return self.user

    def pyrogram_client(self, proxy=None, no_updates=True):
        client = self.pyrogram_session.client(
            api_id=self.api.api_id,
            api_hash=self.api.api_hash,
            app_version=self.api.app_version,
            device_model=self.api.device_model,
            system_version=self.api.system_version,
            lang_code=self.api.lang_code,
            proxy=proxy,
            no_updates=no_updates,
        )
        return client

    def telethon_client(self, proxy=None, no_updates=True):
        client = self.telethon_session.client(
            api_id=self.api.api_id,
            api_hash=self.api.api_hash,
            app_version=self.api.app_version,
            device_model=self.api.device_model,
            system_version=self.api.system_version,
            lang_code=self.api.lang_code,
            system_lang_code=self.api.system_lang_code,
            proxy=proxy,
            no_updates=no_updates,
        )
        return client

    def to_pyrogram_string(self) -> str:
        return self.pyrogram_session.to_string()

    async def to_pyrogram_file(self, path: "Path"):
        await self.pyrogram_session.to_file(path)

    def to_telethon_string(self) -> str:
        return self.telethon_session.to_string()

    async def to_telethon_file(self, path: "Path"):
        await self.telethon_session.to_file(path)

    async def to_tdata_folder(self, path: "Path"):
        await self.get_user_id()
        self.tdata_session.to_tdata(path)

    async def to_tdata_zip(self, path: "Path"):
        await self.get_user_id()
        self.tdata_session.to_tdata_zip(path)
