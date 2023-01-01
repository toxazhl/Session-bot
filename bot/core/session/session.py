import zipfile
from pathlib import Path
from secrets import token_urlsafe
from typing import Type
from uuid import UUID

from opentele.api import API, APIData
from pyrogram.errors.rpc_error import RPCError

from bot.core.db.models import Proxy, Session
from bot.core.db.repo import Repo

from .enums import SessionSource
from .files import FileManager
from .kinds.pyro import PyroSession
from .kinds.tdata import TDataSession
from .kinds.tele import TeleSession


class SessionManager:
    def __init__(
        self,
        dc_id: int,
        auth_key: bytes,
        user_id: None | int = None,
        valid: None | bool = None,
        api: Type[APIData] = API.TelegramDesktop,
        proxy: None | Proxy = None,
        first_name: None | str = None,
        last_name: None | str = None,
        username: None | str = None,
        phone: None | str = None,
        filename: None | str = None,
        source: None | SessionSource = None,
    ):
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.user_id = user_id
        self.valid = valid
        self.api = api.Generate()
        self.proxy = proxy
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.filename = filename
        self.source = source
        self.user = None
        self.client = None

    async def __aenter__(self):
        self.client = self.pyrogram_client()
        await self.client.connect()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()
        self.client = None

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
    async def autoimport(cls, file: Path, filename: None | str = None) -> None | str:
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
    async def from_database(
        cls, session_id: UUID, repo: Repo, proxy: None | Proxy = None
    ):
        session = await repo.session.get(session_id)
        return cls.from_session(session, proxy)

    @classmethod
    def from_session(cls, session: Session, proxy: None | Proxy = None):
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
            proxy=proxy,
        )

    @classmethod
    async def from_telethon_file(
        cls, file: Path, filename: None | str = None, api=API.TelegramDesktop
    ):
        session = await TeleSession.from_file(file)
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            api=api,
            filename=filename,
            source=SessionSource.TELETHON_FILE,
        )

    @classmethod
    def from_telethon_string(cls, string: str, api=API.TelegramDesktop):
        session = TeleSession.from_string(string)
        return cls(
            dc_id=session.dc_id,
            auth_key=session.auth_key,
            api=api,
            source=SessionSource.TELETHON_STRING,
        )

    @classmethod
    async def from_pyrogram_file(
        cls, file: Path, filename: None | str = None, api=API.TelegramDesktop
    ):
        session = await PyroSession.from_file(file)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            api=api,
            user_id=session.user_id,
            filename=filename,
            source=SessionSource.PYROGRAM_FILE,
        )

    @classmethod
    def from_pyrogram_string(cls, string: str, api=API.TelegramDesktop):
        session = PyroSession.from_string(string)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            api=api,
            user_id=session.user_id,
            source=SessionSource.PYROGRAM_STRING,
        )

    @classmethod
    def from_tdata_folder(cls, folder: Path):
        session = TDataSession.from_tdata(folder)
        return cls(
            auth_key=session.auth_key,
            dc_id=session.dc_id,
            api=session.api,
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

    async def to_tdata_folder(self, path: Path):
        await self.get_user_id()
        self.tdata.to_folder(path)

    async def to_tdata_zip(self, path: Path):
        await self.get_user_id()
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
        return TDataSession(
            dc_id=self.dc_id,
            auth_key=self.auth_key,
            api=self.api,
            user_id=self.user_id,
        )

    def pyrogram_client(self, proxy=None, no_updates=True):
        if self.proxy and not proxy:
            proxy = self.proxy.pyro_format()

        client = self.pyrogram.client(
            api=self.api,
            proxy=proxy,
            no_updates=no_updates,
        )
        return client

    def telethon_client(self, proxy=None, no_updates=True):
        client = self.telethon.client(
            api=self.api,
            proxy=proxy or self.proxy,
            no_updates=no_updates,
        )
        return client

    async def validate(self) -> bool:
        try:
            user = await self.get_user()

        except RPCError:
            self.valid = False

        else:
            self.valid = True
            self.first_name = user.first_name
            self.last_name = user.last_name
            self.username = user.username
            self.phone = user.phone_number

        return self.valid

    async def get_user_id(self):
        if self.user_id:
            return self.user_id

        user = await self.get_user()

        if user is None:
            raise TypeError()

        return user.id

    async def get_user(self):
        async with self as client:
            self.user = await client.get_me()
            if self.user:
                self.user_id = self.user.id
        return self.user
