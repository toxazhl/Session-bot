from typing import TYPE_CHECKING

from opentele.api import API
from opentele.td import TDesktop, Account, AuthKeyType, AuthKey
from opentele.td.configs import DcId, BuiltInDc

from bot.core.sessions.filemanager import FileManager

if TYPE_CHECKING:
    from pathlib import Path
    from opentele.api import APIData
    from typing import Type


class TDataSession:
    def __init__(
        self,
        *,
        dc_id: int,
        auth_key: bytes,
        user_id: int,
        api: "Type[APIData]" = API.TelegramDesktop,
    ):
        self.api = api
        self.auth_key = auth_key
        self.user_id = user_id
        self.dc_id = dc_id
        dc = [dc for dc in BuiltInDc.kBuiltInDcs if dc.id == DcId(dc_id)][0]
        self.dc_id, self.server_address, self.port = dc.id, dc.ip, dc.port

    @classmethod
    def from_tdata(cls, tdata_folder: "Path"):
        if not tdata_folder.exists():
            raise FileNotFoundError(tdata_folder)

        client = TDesktop(basePath=tdata_folder)
        account = client.mainAccount

        return cls(
            auth_key=account.authKey.key,
            user_id=account.UserId,
            dc_id=account.MainDcId
        )

    def to_tdata(self, path: "Path"):
        path.mkdir(parents=True, exist_ok=True)

        dc_id = DcId(self.dc_id)
        authKey = AuthKey(self.auth_key, AuthKeyType.ReadFromFile, dc_id)

        if self.user_id is None:
            raise ValueError("user_id is None")

        client = TDesktop()
        client._TDesktop__generateLocalKey()
        account = Account(owner=client, api=self.api)
        account._setMtpAuthorizationCustom(dc_id, self.user_id, [authKey])
        client._addSingleAccount(account)

        client.SaveTData(path / "tdata")

    def to_tdata_zip(self, path: "Path"):
        with FileManager() as fm:
            self.to_tdata(fm.path)
            fm.zip(path)
