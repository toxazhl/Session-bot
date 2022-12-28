import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.markdown import hcode

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.sessions.manager import SessionManager
from bot.core.sessions.filemanager import FileManager
from bot.misc.cd_data import SessionCb

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(SessionCb.filter(F.action == "pyro_sql"))
async def to_pyro_sql_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    try:
        session_id = callback_data.session_id
        manager = await SessionManager.from_database(session_id, repo)
        print(manager.user_id)

        with FileManager(suffix=".session") as fm:
            await manager.to_pyrogram_file(fm.path)
            await query.message.answer_document(
                FSInputFile(fm.path, filename=f"pyrogram-{fm.name}")
            )

        return await query.answer()
    except Exception as e:
        logger.exception(e)
        return query.answer(f"Не удалось скоnвертировать сессию. {e}")


@router.callback_query(SessionCb.filter(F.action == "pyro_str"))
async def to_pyro_str_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    try:
        session_id = callback_data.session_id
        manager = await SessionManager.from_database(session_id, repo)

        string_session = manager.to_pyrogram_string()
        await query.message.edit_text(
            hcode(string_session),
            reply_markup=kb.sessions.back_to_session(session_id),
        )
        return await query.answer()
    except Exception as e:
        logger.exception(e)
        return query.answer(f"Не удалось скоnвертировать сессию. {e}")


@router.callback_query(SessionCb.filter(F.action == "tele_sql"))
async def to_tele_sql_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    try:
        session_id = callback_data.session_id
        manager = await SessionManager.from_database(session_id, repo)

        with FileManager(suffix=".session") as fm:
            await manager.to_telethon_file(fm.path)
            await query.message.answer_document(
                FSInputFile(fm.path, filename=f"telethon-{fm.name}")
            )

        return await query.answer()
    except Exception as e:
        logger.exception(e)
        return query.answer(f"Не удалось скоnвертировать сессию. {e}")


@router.callback_query(SessionCb.filter(F.action == "tele_str"))
async def to_tele_str_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    try:
        session_id = callback_data.session_id
        manager = await SessionManager.from_database(session_id, repo)

        string_session = manager.to_telethon_string()
        await query.message.edit_text(
            hcode(string_session),
            reply_markup=kb.sessions.back_to_session(session_id),
        )
        return await query.answer()
    except Exception as e:
        logger.exception(e)
        return query.answer(f"Не удалось скоnвертировать сессию. {e}")


@router.callback_query(SessionCb.filter(F.action == "tdata_zip"))
async def to_tdata_zip_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    try:
        session_id = callback_data.session_id
        manager = await SessionManager.from_database(session_id, repo)

        with FileManager(suffix=".zip") as fm:
            await manager.to_tdata_zip(fm.path)
            await query.message.answer_document(
                FSInputFile(fm.path, filename=f"tdata-{fm.name}")
            )

        return await query.answer()
    except TypeError:
        return query.answer("Для конвертации в tdata сессия должна быть валидной")

    except Exception as e:
        logger.exception(e)
        return query.answer(f"Не удалось скоnвертировать сессию. {e}")
