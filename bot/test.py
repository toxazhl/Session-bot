import asyncio

import aiohttp
from aio_crystal_pay import CrystalPay


async def main():
    # client = CrystalPay(
    #     "telesession",
    #     "6459486949ca437201cc7d9c03ca84a8fbe93752",
    #     "f85b096411d65b5fc4dcfe9b47a277269701af46",
    # )

    data = {
        "o": "invoice-create",
        "n": "telesession",
        "s": "6459486949ca437201cc7d9c03ca84a8fbe93752",
        "amount": 5,
        "currency": "USD",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.crystalpay.ru/v1/", params=data) as r:
            print(await r.json())


asyncio.run(main())
