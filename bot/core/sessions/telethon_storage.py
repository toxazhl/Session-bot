from pathlib import Path
import os

from telethon import TelegramClient
from telethon.sessions import Session, SQLiteSession, StringSession
from telethon.crypto import AuthKey

from .base import BaseSession


class TeleSession(BaseSession):
    def __init__(
        self,
        name: None | str = None,
        *,
        auth_key: bytes,
        dc_id: int,
        port: int,
        server_address: str,
    ):
        super().__init__(name)
        self.auth_key = auth_key
        self.dc_id = dc_id
        self.port = port
        self.server_address = server_address

    @classmethod
    async def from_Session(cls, Session: Session):
        return cls(
            auth_key=Session.auth_key,
            dc_id=Session.dc_id,
            port=Session.port,
            server_address=Session.server_address,
        )

    @classmethod
    async def from_string(cls, session_string: str):
        Session = StringSession(session_string)
        return await cls.from_Session(Session)

    @classmethod
    async def from_file(cls, file: str | Path):
        file = Path(file)
        if not file.is_file():
            raise FileNotFoundError(file)

        Session = SQLiteSession(file)
        return await cls.from_Session(Session)

    async def get_client(
        self,
        api_id: int,
        api_hash: str,
        app_version: None | str = None,
        device_model: None | str = None,
        system_version: None | str = None,
        lang_code: None | str = None,
        system_lang_code: None | str = None,
        proxy: None | dict = None,
        no_updates: bool = True
    ) -> TelegramClient:
        client = TelegramClient(
            session=StringSession(await self.to_string()),
            api_id=api_id,
            api_hash=api_hash,
            proxy=proxy,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
            receive_updates=not no_updates,
        )
        await client.start()
        return client

    async def save_to_Session(self, Session: Session) -> None:
        Session.set_dc(self.dc_id, self.server_address, self.port)
        Session.auth_key = AuthKey(self.auth_key)

    async def to_string(self) -> str:
        Session = StringSession()
        await self.save_to_Session(Session)
        return Session.save()

    async def to_file(self) -> str | Path:
        os.makedirs(os.path.dirname(self.SESSION_PATH), exist_ok=True)
        Session = SQLiteSession(self.SESSION_PATH / self.name)
        await self.save_to_Session(Session)
        Session.save()
        Session.close()
        return Session.filename
