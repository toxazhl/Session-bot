from typing import TYPE_CHECKING

from opentele.api import API
from opentele.td import TDesktop, Account, AuthKeyType, AuthKey
from opentele.td.configs import DcId

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
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.user_id = user_id
        self.api = api

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

    def to_folder(self, path: "Path"):
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

    def to_zip(self, path: "Path"):
        with FileManager() as fm:
            self.to_folder(fm.path)
            fm.zip(path)
