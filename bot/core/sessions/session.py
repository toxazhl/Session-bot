from pathlib import Path
from typing import Type

from opentele.api import API, APIData

from .pyrogram_session import PyroSession
from .telethon_storage import TeleSession
from .tdata_session import TDataSession


class TelegramSession:
    def __init__(
        self,
        auth_key: bytes,
        dc_id: int,
        port: int,
        server_address: str,
        api: Type[APIData] = API.TelegramDesktop,
        is_bot: None | bool = None,
        test_mode: None | bool = None,
        user_id: None | int = None,
    ):
        self._auth_key = auth_key
        self._dc_id = dc_id
        self._is_bot = is_bot
        self._server_address = server_address
        self._test_mode = test_mode
        self._user_id = user_id
        self._port = port
        self._api = api

    @classmethod
    async def from_telethon_session(
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
    async def from_telethon_file(
        cls, file: str | Path, api=API.TelegramDesktop
    ):
        session = await TeleSession.from_file(file)
        return await cls.from_telethon_session(session, api=api)

    @classmethod
    async def from_telethon_string(cls, string: str, api=API.TelegramDesktop):
        session = await TeleSession.from_string(string)
        return await cls.from_telethon_session(session, api=api)

    @classmethod
    async def from_pyrogram_session(
        cls, session: PyroSession, api=API.TelegramDesktop
    ):
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            port=session.port,
            server_address=session.server_address,
            api=api,
            is_bot=session.is_bot,
            test_mode=session.test_mode,
            user_id=session.user_id,
        )

    @classmethod
    async def from_pyrogram_file(
        cls, file: str | Path, api=API.TelegramDesktop
    ):
        session = await PyroSession.from_file(file)
        return await cls.from_pyrogram_session(session, api=api)

    @classmethod
    async def from_pyrogram_string(cls, string: str, api=API.TelegramDesktop):
        session = await PyroSession.from_string(string)
        return await cls.from_pyrogram_session(session, api=api)

    @classmethod
    async def from_tdata_folder(cls, folder: str | Path):
        session = await TDataSession.from_tdata(folder)
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
            api_id=self._api.api_id,
            auth_key=self._auth_key,
            dc_id=self._dc_id,
            is_bot=self._is_bot or False,
            test_mode=self._test_mode or False,
            user_id=self._user_id or 0,
        )

    @property
    def telethon_session(self) -> TeleSession:
        return TeleSession(
            auth_key=self._auth_key,
            dc_id=self._dc_id,
            port=self._port,
            server_address=self._server_address,
        )

    @property
    def tdata_session(self) -> TDataSession:
        return TDataSession(
            api=self._api,
            auth_key=self._auth_key,
            user_id=self._user_id,
            dc_id=self._dc_id,
        )

    async def update_user_id(self):
        if self._user_id is None:
            client = await self.get_telethon_client()
            user = await client.get_me()
            if user is None:
                raise ValueError("Could not get user id")

            self._user_id = user.id

    async def get_pyrogram_client(self, proxy=None, no_updates=True):
        client = await self.pyrogram_session.get_client(
            api_id=self._api.api_id,
            api_hash=self._api.api_hash,
            app_version=self._api.app_version,
            device_model=self._api.device_model,
            system_version=self._api.system_version,
            lang_code=self._api.lang_code,
            proxy=proxy,
            no_updates=no_updates,
        )
        return client

    async def get_telethon_client(self, proxy=None, no_updates=True):
        client = await self.telethon_session.get_client(
            api_id=self._api.api_id,
            api_hash=self._api.api_hash,
            app_version=self._api.app_version,
            device_model=self._api.device_model,
            system_version=self._api.system_version,
            lang_code=self._api.lang_code,
            system_lang_code=self._api.system_lang_code,
            proxy=proxy,
            no_updates=no_updates,
        )
        return client

    async def to_pyrogram_string(self) -> str:
        await self.update_user_id()
        return await self.pyrogram_session.to_string()

    async def to_pyrogram_file(self) -> str | Path:
        await self.update_user_id()
        return await self.pyrogram_session.to_file()

    async def to_telethon_string(self) -> str | Path:
        return await self.telethon_session.to_string()

    async def to_telethon_file(self) -> str | Path:
        return await self.telethon_session.to_file()

    async def to_tdata_folder(self) -> str | Path:
        await self.update_user_id()
        return await self.tdata_session.to_tdata()
