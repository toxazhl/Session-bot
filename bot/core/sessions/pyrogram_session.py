from pathlib import Path
import os

from pyrogram.client import Client
from pyrogram.storage.memory_storage import MemoryStorage
from pyrogram.storage.file_storage import FileStorage
from pyrogram.storage.storage import Storage
from pyrogram.session.internals.data_center import DataCenter

from .base import BaseSession


class PyroSession(BaseSession):
    def __init__(
        self,
        name: None | str = None,
        *,
        api_id: int,
        auth_key: bytes,
        dc_id: int,
        is_bot: bool,
        test_mode: bool,
        user_id: int,
    ):
        super().__init__(name)
        self.api_id = api_id
        self.auth_key = auth_key
        self.dc_id = dc_id
        self.is_bot = is_bot
        self.test_mode = test_mode
        self.user_id = user_id
        self.server_address, self.port = DataCenter(
            dc_id=dc_id,
            test_mode=False,
            ipv6=False,
            media=False
        )

    @classmethod
    async def from_Session(cls, session: Storage):
        return cls(
            api_id=await session.api_id(),
            auth_key=await session.auth_key(),
            dc_id=await session.dc_id(),
            is_bot=await session.is_bot(),
            test_mode=await session.test_mode(),
            user_id=await session.user_id(),
        )

    @classmethod
    async def from_string(cls, session_string: str):
        session = MemoryStorage(cls.new_name(), session_string)
        await session.open()
        return await cls.from_Session(session)

    @classmethod
    async def from_file(cls, file: str | Path):
        file = Path(file)
        if not file.is_file():
            raise FileNotFoundError(file)

        session = FileStorage(cls.new_name(), cls.SESSION_PATH)
        session.database = file
        await session.open()
        return await cls.from_Session(session)

    async def get_client(
        self,
        api_id: int,
        api_hash: str,
        app_version: None | str = None,
        device_model: None | str = None,
        system_version: None | str = None,
        lang_code: None | str = None,
        proxy: None | dict = None,
        no_updates: bool = True
    ) -> Client:
        client = Client(
            name=self.name,
            api_id=api_id,
            api_hash=api_hash,
            app_version=app_version,
            device_model=device_model,
            system_version=system_version,
            lang_code=lang_code,
            proxy=proxy,
            session_string=await self.to_string(),
            no_updates=no_updates,
            test_mode=self.test_mode,
            workdir=self.SESSION_PATH
        )
        await client.start()
        return client

    async def save_to_Session(self, session: Storage) -> None:
        await session.open()
        await session.dc_id(self.dc_id)
        await session.api_id(self.api_id)
        await session.test_mode(self.test_mode)
        await session.auth_key(self.auth_key)
        await session.user_id(self.user_id)
        await session.is_bot(self.is_bot)
        await session.date(0)

    async def to_string(self) -> str:
        session = MemoryStorage(self.name)
        await self.save_to_Session(session)
        return await session.export_session_string()

    async def to_file(self) -> str | Path:
        os.makedirs(self.SESSION_PATH, exist_ok=True)
        session = FileStorage(self.name, self.SESSION_PATH)
        await self.save_to_Session(session)
        await session.save()
        await session.close()
        return session.database
