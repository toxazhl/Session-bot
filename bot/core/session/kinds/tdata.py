from pathlib import Path
from typing import Type

from opentele.api import API, APIData
from opentele.exception import TFileNotFound
from opentele.td import Account, AuthKey, AuthKeyType, TDesktop
from opentele.td.configs import DcId

from bot.core.session.exceptions import TFileError
from bot.core.session.files import FileManager


class TDataSession:
    def __init__(
        self,
        *,
        dc_id: int,
        auth_key: bytes,
        user_id: int,
        # api: Type[APIData] = API.TelegramDesktop,
    ):
        self.dc_id = dc_id
        self.auth_key = auth_key
        self.user_id = user_id
        # self.api = api

    @classmethod
    def from_tdata(cls, tdata_folder: Path):
        try:
            client = TDesktop(basePath=tdata_folder)
        except TFileNotFound:
            raise TFileError

        return cls(
            auth_key=client.mainAccount.authKey.key,
            user_id=client.mainAccount.UserId,
            dc_id=client.mainAccount.MainDcId,
        )

    def to_folder(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

        dc_id = DcId(self.dc_id)
        authKey = AuthKey(self.auth_key, AuthKeyType.ReadFromFile, dc_id)

        if self.user_id is None:
            raise ValueError("user_id is None")

        client = TDesktop()
        client._TDesktop__generateLocalKey()
        # account = Account(owner=client, api=self.api)
        account = Account(owner=client)
        account._setMtpAuthorizationCustom(dc_id, self.user_id, [authKey])
        client._addSingleAccount(account)

        client.SaveTData(path / "tdata")

    def to_zip(self, path: Path):
        with FileManager() as fm:
            self.to_folder(fm.path)
            fm.zip(path)
