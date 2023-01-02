import hashlib
import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class CrystalPay:
    API_URL = "https://api.crystalpay.ru/v1/"

    def __init__(
        self, name: str, secret1: str, secret2: str, callback: None | str = None
    ):
        self.name = name
        self.secret1 = secret1
        self.secret2 = secret2
        self.callback = callback
        self.session = aiohttp.ClientSession()

    def check_hash(self, params: dict[str, Any]) -> bool:
        check_hash = hashlib.sha1(
            f"{params['ID']}:{params['CURRENCY']}:{self.secret2}".encode("utf-8")
        ).hexdigest()
        return check_hash == params["HASH"]

    def prepare_params(self, params: dict[str, Any]) -> dict[str, Any]:
        params.update(s=self.secret1, n=self.name)
        return {k: v for k, v in params.items() if v is not None}

    async def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        async with self.session.get(self.API_URL, params=params) as resp:
            return await resp.json()

    async def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        params = self.prepare_params(params)
        logger.debug(f"Create invoice params: {params}")
        return await self._get(params)

    async def invoice_create(
        self,
        amount: float,
        m: None | str = None,
        currency: None | str = None,
        lifetime: None | int = None,
        redirect: None | str = None,
        callback: None | str = None,
        extra: None | str = None,
    ):
        params = dict(
            o="invoice-create",
            amount=amount,
            m=m,
            currency=currency,
            lifetime=lifetime,
            redirect=redirect,
            callback=callback or self.callback,
            extra=extra,
        )
        return await self._request(params)

    # @staticmethod
    # def _create_secret_hash(*args):
    #     return hashlib.md5(
    #         "@".join([str(elem) for elem in args]).encode()
    #     ).hexdigest()  # nosec: B303

    # async def create_receipt(
    #     self, amount, lifetime, extra=None, callback=None, redirect=None, currency=None
    # ):
    #     operation = "receipt-create"
    #     params = self.get_params(
    #         o=operation,
    #         amount=amount,
    #         lifetime=lifetime,
    #         extra=extra or None,
    #         callback=callback or None,
    #         redirect=redirect or None,
    #     )
    #     response = await self._request("GET", params)
    #     if currency:
    #         response["url"] = response["url"] + "&m=" + currency
    #     return response

    # async def check_receipt(self, receipt_id):
    #     return await self._request(
    #         "GET", self.get_params(o="receipt-check", i=receipt_id)
    #     )

    # async def get_balance(self):
    #     return await self._request("GET", self.get_params(o="balance"))

    # async def create_withdraw(self, amount, currency, wallet, callback=None):
    #     operation = "withdraw"
    #     withdraw_secret = self._create_secret_hash(wallet, amount, self.secret2)
    #     params = self.get_params(
    #         o=operation,
    #         secret=withdraw_secret,
    #         amount=amount,
    #         wallet=wallet,
    #         currency=currency,
    #         callback=callback or None,
    #     )
    #     return await self._request("GET", params)

    # async def check_withdraw(self, withdraw_id):
    #     operation = "withdraw-status"
    #     params = self.get_params(o=operation, i=withdraw_id)
    #     return await self._request("GET", params)

    # async def p2p_transfer(self, login, amount, currency):
    #     operation = "p2p-transfer"
    #     p2p_secret = self._create_secret_hash(currency, amount, login, self.secret2)
    #     params = self.get_params(
    #         o=operation,
    #         secret=p2p_secret,
    #         login=login,
    #         amount=amount,
    #         currency=currency,
    #     )
    #     return await self._request("GET", params)

    # async def create_voucher(self, amount, currency, comment=None):
    #     operation = "voucher-create"
    #     voucher_secret = self._create_secret_hash(currency, amount, self.secret2)

    #     kwargs = {"o": operation, "secret": voucher_secret}
    #     if comment is not None:
    #         kwargs["comment"] = comment

    #     return await self._request("GET", self.get_params(**kwargs))

    # async def voucher_info(self, voucher_code):
    #     operation = "voucher-info"
    #     params = self.get_params(o=operation, code=voucher_code)
    #     return await self._request("GET", params)

    # async def activate_voucher(self, voucher_code):
    #     return await self._request(
    #         "GET", self.get_params(o="voucher-activate", code=voucher_code)
    #     )

    # def generate_payment_hash(
    #     self, payment_id: typing.Union[int, str], currency: str
    # ) -> str:
    #     hash_object = hashlib.sha1(
    #         "{}:{}:{}".format(payment_id, currency, self.secret2).encode()
    #     )
    #     return hash_object.hexdigest()
