import asyncio
import logging.config
import yaml
import os

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bot.core.config.configreader import Config
from bot.handlers import setup_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.user import UserMiddleware


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    with open("bot/core/config/logging.yaml", "r") as stream:
        logging_config = yaml.load(stream, Loader=yaml.FullLoader)

    for handler in logging_config["handlers"].values():
        if log_filename := handler.get("filename"):
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    logging.config.dictConfig(logging_config)


async def main():
    setup_logging()

    logger = logging.getLogger(__name__)

    config = Config()

    engine = create_async_engine(config.postgres_dsn, future=True)
    db_pool = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    bot = Bot(token=config.bot.token, parse_mode="HTML")

    if config.bot.use_redis:
        dp = Dispatcher(storage=RedisStorage.from_url(config.redis_dsn))
    else:
        dp = Dispatcher(storage=MemoryStorage())

    dp.message.filter(F.chat.type == "private")

    dp.update.outer_middleware(DbSessionMiddleware(db_pool))
    dp.update.outer_middleware(UserMiddleware())

    router = setup_routers()
    dp.include_router(router)

    try:
        if not config.web.enable_webhook:
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
            )
        else:
            app = web.Application()

            me = await bot.get_me()
            url = f"{config.web.domain}{config.web.path.bot}"
            logger.info(
                f"Run webhook for bot https://t.me/{me.username} "
                f'id={bot.id} - "{me.full_name}" on {url}'
            )

            await bot.set_webhook(
                url=url,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(
                app, path=config.web.path.bot
            )

            # Creating aiohttp server
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, config.web.host, config.web.port)
            logger.info(f"Running app on {config.web.host}:{config.web.port}")
            await site.start()

            await asyncio.Event().wait()

    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
