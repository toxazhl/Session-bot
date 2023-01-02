import logging
from sqlite3 import DatabaseError
from zipfile import BadZipFile

from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent

from bot.core.session.exceptions import ClientNotFoundError, TFileError, ValidationError

logger = logging.getLogger(__name__)

router = Router()


async def update_answer(error: ErrorEvent, text: str):
    if error.update.callback_query:
        await error.update.callback_query.answer(text)

    elif error.update.message:
        await error.update.message.answer(text)


@router.errors(ExceptionTypeFilter(DatabaseError, ValidationError))
async def error_session_handler(error: ErrorEvent):
    await update_answer(error, "❌ Файл не является выбраным типом сессии")


@router.errors(ExceptionTypeFilter(BadZipFile))
async def error_zip_handler(error: ErrorEvent):
    await update_answer(error, "❌ Файл не является zip архивом")


@router.errors(ExceptionTypeFilter(TFileError))
async def error_key_datahandler(error: ErrorEvent):
    await update_answer(error, "❌ Не удалось открыть key_data")


@router.errors(ExceptionTypeFilter(ClientNotFoundError))
async def error_client_not_foundhandler(error: ErrorEvent):
    await update_answer(error, "❌ Всемя жизни клиента вышло. Попробуйте еще раз")


@router.errors()
async def error_handler(error: ErrorEvent):
    await update_answer(
        error,
        "❌ Произошла ошибка",
    )
    raise error.exception
