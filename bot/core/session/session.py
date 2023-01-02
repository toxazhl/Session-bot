import zipfile
from pathlib import Path
from secrets import token_urlsafe
from typing import Type
from uuid import UUID

from opentele.api import APIData
from pyrogram.errors.rpc_error import RPCError
from typing_extensions import Self

from bot.core.db.models import Session
from bot.core.db.repo import Repo

from .client import Client, ClientManager
from .enums import SessionSource
from .exceptions import ClientManagerNotInitialized, UserIdNoneError
from .files import FileManager
from .kinds.pyro import PyroSession
from .kinds.tdata import TDataSession
from .kinds.tele import TeleSession

# api: Type[APIData] | APIData


class SessionManager:
    def __init__(
        self,
        dc_id: int,
        auth_key: bytes,
        user_id: None | int = None,
        valid: None | bool = None,
        first_name: None | str = None,
        last_name: None | str = None,
        username: None | str = None,
        phone: None | str = None,
        filename: None | str = None,
        source: None | SessionSource = None,
        client_manager: None | ClientManager = None,
    ):
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.user_id = user_id
        self.valid = valid
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.filename = filename
        self.source = source
        self.client_manager = client_manager
        self.user = None

    def client(self, api: Type[APIData] | APIData, no_updates: None | bool = None):
        if self.client_manager is None:
            raise ClientManagerNotInitialized

        return self.client_manager.new(
            api_id=api.api_id,
            api_hash=api.api_hash,
            app_version=api.app_version,
            device_model=api.device_model,
            system_version=api.system_version,
            lang_code=api.lang_code,
            session_string=self.pyrogram.to_string(),
            no_updates=no_updates,
        )

    @property
    def auth_key_hex(self) -> str:
        return self.auth_key.hex()

    @property
    def name(self) -> str:
        if self.filename:
            return self.filename
        if self.username:
            return f"@{self.username}"
        if self.first_name and self.last_name:
            return f"{self.first_name}_{self.last_name}"
        if self.first_name:
            return f"{self.first_name}"
        if self.user_id:
            return str(self.user_id)
        return token_urlsafe(4)

    @classmethod
    async def autoimport(cls, file: Path, filename: None | str = None) -> None | Self:
        if await PyroSession.validate(file):
            return await cls.from_pyrogram_file(file, filename)
        if await TeleSession.validate(file):
            return await cls.from_telethon_file(file, filename)

        try:
            with FileManager() as fm:
                with zipfile.ZipFile(file) as f:
                    f.extractall(fm.path)

                if fm.path.joinpath("tdata").exists():
                    tdata_path = fm.path.joinpath("tdata")
                else:
                    tdata_path = fm.path

                return SessionManager.from_tdata_folder(tdata_path)

        except Exception:
            return None

    @classmethod
    async def from_database(cls, session_id: UUID, repo: Repo):
        session = await repo.session.get(session_id)
        return cls.from_session(session)

    @classmethod
    def from_session(cls, session: Session):
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            user_id=session.telegram_id,
            valid=session.valid,
            first_name=session.first_name,
            last_name=session.last_name,
            username=session.username,
            phone=session.phone,
            filename=session.filename,
        )

    @classmethod
    async def from_telethon_file(cls, file: Path, filename: None | str = None):
        session = await TeleSession.from_file(file)
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            filename=filename,
            source=SessionSource.TELETHON_FILE,
        )

    @classmethod
    def from_telethon_string(cls, string: str):
        session = TeleSession.from_string(string)
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            source=SessionSource.TELETHON_STRING,
        )

    @classmethod
    async def from_pyrogram_file(cls, file: Path, filename: None | str = None):
        session = await PyroSession.from_file(file)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            user_id=session.user_id,
            filename=filename,
            source=SessionSource.PYROGRAM_FILE,
        )

    @classmethod
    def from_pyrogram_string(cls, string: str):
        session = PyroSession.from_string(string)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            user_id=session.user_id,
            source=SessionSource.PYROGRAM_STRING,
        )

    @classmethod
    def from_tdata_folder(cls, folder: Path):
        session = TDataSession.from_tdata(folder)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            # api=session.api,
            filename=folder.name,
            source=SessionSource.TDATA,
        )

    async def to_pyrogram_file(self, path: Path):
        await self.pyrogram.to_file(path)

    def to_pyrogram_string(self) -> str:
        return self.pyrogram.to_string()

    async def to_telethon_file(self, path: Path):
        await self.telethon.to_file(path)

    def to_telethon_string(self) -> str:
        return self.telethon.to_string()

    def to_tdata_folder(self, path: Path):
        self.tdata.to_folder(path)

    def to_tdata_zip(self, path: Path):
        self.tdata.to_zip(path)

    @property
    def pyrogram(self) -> PyroSession:
        return PyroSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            user_id=self.user_id,
        )

    @property
    def telethon(self) -> TeleSession:
        return TeleSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
        )

    @property
    def tdata(self) -> TDataSession:
        if self.user_id is None:
            raise UserIdNoneError

        return TDataSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            # api=self.api,
            user_id=self.user_id,
        )

    # def pyrogram_client(self, proxy=None, no_updates=True):
    #     if self.proxy and not proxy:
    #         proxy = self.proxy.pyro_format()

    #     client = self.pyrogram.client(
    #         api=self.api,
    #         proxy=proxy,
    #         no_updates=no_updates,
    #     )
    #     return client

    # def telethon_client(self, proxy=None, no_updates=True):
    #     client = self.telethon.client(
    #         api=self.api,
    #         proxy=proxy or self.proxy,
    #         no_updates=no_updates,
    #     )
    #     return client

    async def validate(
        self, client_manager: ClientManager, api: Type[APIData] | APIData
    ) -> bool:
        try:
            async with client_manager.new(
                api_id=api.api_id,
                api_hash=api.api_hash,
                app_version=api.app_version,
                device_model=api.device_model,
                system_version=api.system_version,
                lang_code=api.lang_code,
                session_string=self.to_pyrogram_string(),
                timeout=20,
            ) as client:
                user = await client.get_me()

        except RPCError:
            self.valid = False

        else:
            self.valid = True
            self.user = user
            self.user_id = user.id
            self.first_name = user.first_name
            self.last_name = user.last_name
            self.username = user.username
            self.phone = user.phone_number

        return self.valid
