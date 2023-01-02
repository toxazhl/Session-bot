import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.markdown import hcode

from bot import keyboards as kb
from bot.core.db.repo import Repo
from bot.core.session.files import FileManager
from bot.core.session.session import SessionManager
from bot.misc.cd_data import SessionCb

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(SessionCb.filter(F.action == "pyro_sql"))
async def to_pyro_sql_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)
    manager.filename
    with FileManager(suffix=".session") as fm:
        await manager.to_pyrogram_file(fm.path)
        await query.message.answer_document(
            FSInputFile(fm.path, filename=f"pyrogram-{manager.name}{fm.path.suffix}")
        )

    await query.answer()


@router.callback_query(SessionCb.filter(F.action == "pyro_str"))
async def to_pyro_str_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)

    string_session = manager.to_pyrogram_string()
    await query.message.edit_text(
        hcode(string_session),
        reply_markup=kb.sessions.back_to_session(callback_data.session_id),
    )
    await query.answer()


@router.callback_query(SessionCb.filter(F.action == "tele_sql"))
async def to_tele_sql_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)
    with FileManager(suffix=".session") as fm:
        await manager.to_telethon_file(fm.path)
        await query.message.answer_document(
            FSInputFile(fm.path, filename=f"telethon-{manager.name}{fm.path.suffix}")
        )

    await query.answer()


@router.callback_query(SessionCb.filter(F.action == "tele_str"))
async def to_tele_str_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)

    string_session = manager.to_telethon_string()
    await query.message.edit_text(
        hcode(string_session),
        reply_markup=kb.sessions.back_to_session(callback_data.session_id),
    )
    await query.answer()


@router.callback_query(SessionCb.filter(F.action == "tdata_zip"))
async def to_tdata_zip_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)
    if manager.user_id is None:
        await query.answer(
            "Невозможно сконвертировать сессию из-за отсутствия user_id\n"
            'Нажмите на "🔎 Validate" что-бы обновить user_id сессии',
            show_alert=True,
        )
        return

    with FileManager(suffix=".zip") as fm:
        manager.to_tdata_zip(fm.path)
        await query.message.answer_document(
            FSInputFile(fm.path, filename=f"tdata-{manager.name}{fm.path.suffix}")
        )

    await query.answer()
