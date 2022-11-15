import base64
import secrets
import struct
from typing import TYPE_CHECKING

from pyrogram.client import Client
from pyrogram.session.internals.data_center import DataCenter

from .storage import Database

if TYPE_CHECKING:
    from pathlib import Path


class PyroSession:
    OLD_STRING_FORMAT = ">B?256sI?"
    OLD_STRING_FORMAT_64 = ">B?256sQ?"
    STRING_SIZE = 351
    STRING_SIZE_64 = 356
    STRING_FORMAT = ">BI?256sQ?"

    def __init__(
        self,
        *,
        dc_id: int,
        auth_key: bytes,
        api_id: None | int = None,
        user_id: None | int = None,
        is_bot: bool = False,
        test_mode: bool = False,
        **kw
    ):
        self.api_id = api_id or 0
        self.auth_key = auth_key
        self.dc_id = dc_id
        self.is_bot = is_bot or False
        self.test_mode = test_mode or False
        self.user_id = user_id or 0
        self.server_address, self.port = DataCenter(
            dc_id=dc_id,
            test_mode=test_mode,
            ipv6=False,
            media=False
        )

    @classmethod
    def from_string(cls, session_string: str):
        if len(session_string) in [cls.STRING_SIZE, cls.STRING_SIZE_64]:
            string_format = cls.OLD_STRING_FORMAT_64

            if len(session_string) == cls.STRING_SIZE:
                string_format = cls.OLD_STRING_FORMAT

            api_id = None
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                string_format,
                base64.urlsafe_b64decode(
                    session_string + "=" * (-len(session_string) % 4)
                )
            )
        else:
            dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                cls.STRING_FORMAT,
                base64.urlsafe_b64decode(
                    session_string + "=" * (-len(session_string) % 4)
                )
            )

        return cls(
            dc_id=dc_id,
            api_id=api_id,
            auth_key=auth_key,
            user_id=user_id,
            is_bot=is_bot,
            test_mode=test_mode,
        )

    @classmethod
    async def from_file(cls, file: "Path"):
        async with Database(file) as db:
            session = await db.get_session()

        return cls(**session)

    def client(
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
            name=secrets.token_urlsafe(8),
            api_id=api_id,
            api_hash=api_hash,
            app_version=app_version,
            device_model=device_model,
            system_version=system_version,
            lang_code=lang_code,
            proxy=proxy,
            session_string=self.to_string(),
            no_updates=no_updates,
            test_mode=self.test_mode,
        )
        return client

    def to_string(self) -> str:
        packed = struct.pack(
            self.STRING_FORMAT,
            self.dc_id,
            self.api_id,
            self.test_mode,
            self.auth_key,
            self.user_id,
            self.is_bot
        )
        return base64.urlsafe_b64encode(packed).decode().rstrip("=")

    async def to_file(self, path: "Path"):
        async with Database(path, create=True) as db:
            await db.add_session(
                dc_id=self.dc_id,
                auth_key=self.auth_key,
                api_id=self.api_id,
                user_id=self.user_id,
                is_bot=self.is_bot,
                test_mode=self.test_mode
            )
