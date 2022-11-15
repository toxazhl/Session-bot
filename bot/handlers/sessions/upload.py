import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.db.models import User
from bot.core.sessions.manager import SessionManager
from bot.core.sessions.filemanager import FileManager
from bot.misc.states import UploadStates
from .menu import text_session
import zipfile

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "📤 Загрузить сессию")
async def upload_session_handler(message: Message):
    return message.answer(
        "Выберите тип сессии, которую хотите конвертировать",
        reply_markup=kb.sessions.upload()
    )


@router.callback_query(F.data == "upload_session")
async def callback_upload_session_handler(query: CallbackQuery):
    await query.answer()
    return query.message.edit_text(
        "Выберите тип сессии, которую хотите конвертировать",
        reply_markup=kb.sessions.upload()
    )


@router.callback_query(F.data == "upload_pyrogram")
async def upload_pyrogram_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.upload_pyrogram)
    return query.message.edit_text(
        "Отправьте файл или строку сессии Pyrogram",
        reply_markup=kb.sessions.back_to_upload()
    )


@router.callback_query(F.data == "upload_telethon")
async def upload_telethon_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.upload_telethon)
    return query.message.edit_text(
        "Отправьте файл или строку сессии Telethon",
        reply_markup=kb.sessions.back_to_upload()

    )


@router.callback_query(F.data == "upload_tdata")
async def upload_tdata_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.upload_tdata)
    return query.message.answer(
        "Отправьте архив, в котором содержится папка tdata"
    )


@router.callback_query(F.data == "upload_tgnet.dat")
async def upload_tgnetdat_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.upload_tdata)
    return query.answer(
        "tgnet.dat - файл, в котором хранится сессия Telegram на телефоне. \n"
        "Сейчас этот функционал еще не реализован. \n"
        "Если вам нужно это, то сообщите мне",
        show_alert=True
    )


@router.message(F.document, UploadStates.upload_pyrogram)
async def pyro_sqlite_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    try:
        await state.clear()

        with FileManager() as fm:
            await bot.download(message.document, fm.path)
            manager = await SessionManager.from_pyrogram_file(fm.path)

        session = await repo.session.add_from_manager(user.id, manager)

        return message.answer(
            text_session(manager),
            reply_markup=kb.sessions.action(session.id)
        )
    except Exception as e:
        logger.exception(e)
        return message.answer(f"Не удалось загрузить сессию. {e}")


@router.message(F.text, UploadStates.upload_pyrogram)
async def pyro_string_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    try:
        await state.clear()

        manager = SessionManager.from_pyrogram_string(message.text)
        session = await repo.session.add_from_manager(user.id, manager)

        return message.answer(
            text_session(manager),
            reply_markup=kb.sessions.action(session.id)
        )
    except Exception as e:
        logger.exception(e)
        return message.answer(f"Не удалось загрузить сессию. {e}")


@router.message(F.document, UploadStates.upload_telethon)
async def tele_sqlite_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    try:
        await state.clear()
        with FileManager(ext=".session") as fm:
            await bot.download(message.document, fm.path)
            manager = await SessionManager.from_telethon_file(fm.path)

        session = await repo.session.add_from_manager(user.id, manager)

        return message.answer(
            text_session(manager),
            reply_markup=kb.sessions.action(session.id)
        )
    except Exception as e:
        logger.exception(e)
        return message.answer(f"Не удалось загрузить сессию. {e}")


@router.message(F.text, UploadStates.upload_telethon)
async def tele_string_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    try:
        await state.clear()

        manager = SessionManager.from_telethon_string(message.text)
        session = await repo.session.add_from_manager(user.id, manager)

        return message.answer(
            text_session(manager),
            reply_markup=kb.sessions.action(session.id)
        )
    except Exception as e:
        logger.exception(e)
        return message.answer(f"Не удалось загрузить сессию. {e}")


@router.message(F.document, UploadStates.upload_tdata)
async def tdata_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    try:
        await state.clear()
        with FileManager(ext=".zip") as fm:
            await bot.download(message.document, fm.path)
            with FileManager() as fm2:
                with zipfile.ZipFile(fm.path) as f:
                    f.extractall(fm2.path)

                if fm2.path.joinpath("tdata").exists():
                    tdata_path = fm2.path.joinpath("tdata")
                else:
                    tdata_path = fm2.path

                manager = SessionManager.from_tdata_folder(tdata_path)

        session = await repo.session.add_from_manager(user.id, manager)

        return message.answer(
            text_session(manager),
            reply_markup=kb.sessions.action(session.id)
        )
    except Exception as e:
        logger.exception(e)
        return message.answer(f"Не удалось загрузить сессию. {e}")
