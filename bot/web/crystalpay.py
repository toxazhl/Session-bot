import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound
from aiohttp import web

from bot.core.db.repo import Repo
from bot.core.payment.crystalpay import CrystalPay

logger = logging.getLogger(__name__)


async def crystalpay_callback(request: web.Request):
    crystalpay: CrystalPay = request.app["crystalpay"]
    db_pool = request.app["db_pool"]
    bot: Bot = request.app["bot"]

    params = request.rel_url.query
    logger.debug(f"CryspalPay callback: {params}")

    if not crystalpay.check_hash(params):
        logger.error("Bad hash")
        return web.json_response("Bad hash", status=401)

    amount = float(params["AMOUNT"])
    user_id = int(params["EXTRA"])

    async with db_pool() as session:
        repo = Repo(session)
        user = await repo.user.get(user_id)
        user.balance += int(amount * 100)
        await repo.commit(user)

    try:
        await bot.send_message(user.id, f"💰 Ваш баланс пополнен на {amount}$")

    except (TelegramBadRequest, TelegramNotFound):
        pass

    logger.debug(f"Success payment for user {user.id}")

    return web.json_response("ok", status=200)
