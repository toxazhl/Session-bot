from pathlib import Path
from typing import Type

from opentele.api import API, APIData
from opentele.td import TDesktop, Account, AuthKeyType, AuthKey
from opentele.td.configs import DcId, BuiltInDc

from .base import BaseSession


class TDataSession(BaseSession):
    def __init__(
        self,
        name: None | str = None,
        *,
        api: Type[APIData] = API.TelegramDesktop,
        auth_key: bytes,
        user_id: int,
        dc_id: int,
    ):
        super().__init__(name)
        self.api = api
        self.auth_key = auth_key
        self.user_id = user_id
        self.dc_id = dc_id
        dc = [dc for dc in BuiltInDc.kBuiltInDcs if dc.id == DcId(dc_id)][0]
        self.dc_id, self.server_address, self.port = dc.id, dc.ip, dc.port

    @classmethod
    async def from_tdata(cls, tdata_folder: str | Path):
        tdata_folder = Path(tdata_folder)
        if not tdata_folder.exists():
            raise FileNotFoundError(tdata_folder)

        client = TDesktop(basePath=tdata_folder)
        account = client.mainAccount

        return cls(
            auth_key=account.authKey.key,
            user_id=account.UserId,
            dc_id=account.MainDcId
        )

    async def to_tdata(self) -> Path:
        tdata_folder = self.SESSION_PATH / self.name
        tdata_folder.mkdir(parents=True, exist_ok=True)

        dc_id = DcId(self.dc_id)
        authKey = AuthKey(self.auth_key, AuthKeyType.ReadFromFile, dc_id)

        if self.user_id is None:
            raise ValueError("user_id is None")

        client = TDesktop()
        client._TDesktop__generateLocalKey()
        account = Account(owner=client, api=self.api)
        account._setMtpAuthorizationCustom(dc_id, self.user_id, [authKey])
        client._addSingleAccount(account)

        client.SaveTData(tdata_folder / "tdata")

        return tdata_folder
