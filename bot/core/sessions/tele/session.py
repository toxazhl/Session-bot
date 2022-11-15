import base64
import ipaddress
import struct
from typing import TYPE_CHECKING

from telethon import TelegramClient
from telethon.sessions import StringSession

from .storage import Database

if TYPE_CHECKING:
    from pathlib import Path


class TeleSession:
    _STRUCT_PREFORMAT = '>B{}sH256s'
    CURRENT_VERSION = '1'

    def __init__(
        self,
        *,
        auth_key: bytes,
        dc_id: int,
        port: int,
        server_address: str,
        **kw
    ):
        self.auth_key = auth_key
        self.dc_id = dc_id
        self.port = port
        self.server_address = server_address

    @classmethod
    def from_string(cls, string: str):
        string = string[1:]
        ip_len = 4 if len(string) == 352 else 16
        dc_id, ip, port, auth_key = struct.unpack(
            cls._STRUCT_PREFORMAT.format(ip_len), cls.decode(string)
        )
        server_address = ipaddress.ip_address(ip).compressed
        return cls(
            auth_key=auth_key,
            dc_id=dc_id,
            port=port,
            server_address=server_address,
        )

    @classmethod
    async def from_file(cls, file: "Path"):
        async with Database(file) as db:
            session = await db.get_session()

        return cls(**session)

    @staticmethod
    def encode(x: bytes) -> str:
        return base64.urlsafe_b64encode(x).decode('ascii')

    @staticmethod
    def decode(x: str) -> bytes:
        return base64.urlsafe_b64decode(x)

    def client(
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
    ):
        client = TelegramClient(
            session=StringSession(self.to_string()),
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
        return client

    def to_string(self) -> str:
        ip = ipaddress.ip_address(self.server_address).packed
        return self.CURRENT_VERSION + self.encode(struct.pack(
            self._STRUCT_PREFORMAT.format(len(ip)),
            self.dc_id,
            ip,
            self.port,
            self.auth_key
        ))

    async def to_file(self, path: "Path"):
        async with Database(path, create=True) as db:
            await db.add_session(
                dc_id=self.dc_id,
                auth_key=self.auth_key,
                server_address=self.server_address,
                port=self.port,
            )
