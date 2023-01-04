import logging
from sqlite3 import DatabaseError
from zipfile import BadZipFile

from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent
from telethon.errors import RPCError

from bot import keyboards as kb
from bot.core.session.exceptions import ClientNotFoundError, TFileError, ValidationError

logger = logging.getLogger(__name__)

router = Router()


async def update_answer(
    error: ErrorEvent, text: str, reply_markup=None, edit_message: bool = False
):
    if error.update.callback_query:
        if edit_message:
            await error.update.callback_query.message.edit_text(
                text, reply_markup=reply_markup
            )
        else:
            await error.update.callback_query.answer(text)

    elif error.update.message:
        await error.update.message.answer(text, reply_markup=reply_markup)


@router.errors(ExceptionTypeFilter(RPCError))
async def RPCError_handler(error: ErrorEvent):
    await update_answer(
        error,
        f"❌ <b>{error.exception}</b>\n\nПопробуйте еще раз:",
        reply_markup=kb.main_menu.close(),
        edit_message=True,
    )


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
    await update_answer(error, "❌ Время жизни клиента вышло. Попробуйте еще раз")
    raise error.exception


@router.errors()
async def error_handler(error: ErrorEvent):
    await update_answer(
        error,
        "❌ Произошла ошибка",
    )
    raise error.exception
