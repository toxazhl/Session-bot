import logging
import zipfile
<<<<<<< HEAD
=======
from sqlite3 import DatabaseError
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0

from aiogram import Bot, F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.error_event import ErrorEvent

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.db.models import User
<<<<<<< HEAD
=======
from bot.core.sessions.exceptions import ValidationError
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
from bot.core.sessions.filemanager import FileManager
from bot.core.sessions.manager import SessionManager
from bot.misc.states import UploadStates
from .menu import text_session


logger = logging.getLogger(__name__)

router = Router()


<<<<<<< HEAD
@router.message(F.text == "⬆️ Загрузить")
async def upload_session_handler(message: Message):
    await message.answer(
        "Выбери тип сессии, которую хочешь конвертировать\n"
        "Также ты можешь просто отправить файл, затем мы покажем доступные варианты",
        reply_markup=kb.sessions.upload(),
=======
@router.errors(ExceptionTypeFilter(DatabaseError, ValidationError))
async def error_session_handler(error: ErrorEvent):
    await error.update.message.answer("❌ Файл не является сессией Pyrogram")


@router.errors()
async def error_handler(error: ErrorEvent):
    if error.update.callback_query:
        await error.update.callback_query.answer("❌ Произошла ошибка")
    elif error.update.message:
        await error.update.message.answer("❌ Произошла ошибка")
    raise error.exception


@router.message(F.text == "📤 Загрузить сессию")
async def upload_session_handler(message: Message):
    await message.answer(
        "Выберите тип сессии, которую хотите конвертировать",
        reply_markup=kb.sessions.upload()
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.callback_query(F.data == "upload_pyrogram")
async def upload_pyrogram_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.pyrogram)
<<<<<<< HEAD
    await query.message.edit_text("Отправь файл или строку сессии Pyrogram:")
=======
    await query.message.edit_text("Отправьте файл или строку сессии Pyrogram:")
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0


@router.callback_query(F.data == "upload_telethon")
async def upload_telethon_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.telethon)
<<<<<<< HEAD
    await query.message.edit_text("Отправь файл или строку сессии Telethon:")
=======
    await query.message.edit_text("Отправьте файл или строку сессии Telethon:")
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0


@router.callback_query(F.data == "upload_tdata")
async def upload_tdata_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.tdata)
<<<<<<< HEAD
    await query.message.edit_text("Отправь .zip архив сесии tdata:")


@router.callback_query(F.data == "upload_manual")
async def upload_manual_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.manual_auth_key)
    msg = await query.message.edit_text("Отправь auth_key в HEX формате:")
    await state.update_data(message_id=msg.message_id)


@router.message(F.document.file_size > 512000)
async def upload_file_too_big_handler(message: Message):
    await message.delete()
    await message.answer(
        "❌ Файл слишком большой (> 500 КБ), попробуй очистить его\n"
        "Если это сессия Pyrogram - очисти таблицу <code>peers</code>\n"
        "Если это сессия Telethon - очисти таблицу <code>entities</code>\n"
        "Если это архив с TData - убедись что там нету самого приложения Telegram или очисти кеш"
    )


=======
    await query.message.edit_text("Отправьте zip архив сесии tdata:")


@router.callback_query(F.data == "upload_tgnet.dat")
async def upload_tgnetdat_handler(query: CallbackQuery):
    await query.answer(
        "tgnet.dat - файл, в котором хранится сессия Telegram на телефоне. \n"
        "Сейчас этот функционал еще не реализован. \n"
        "Если вам нужно это, то сообщите мне",
        show_alert=True
    )


@router.callback_query(F.data == "upload_manual")
async def upload_manual_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.manual_auth_key)
    msg = await query.message.edit_text("Отправьте auth_key в HEX формате:")
    await state.update_data(message_id=msg.message_id)


@router.message(F.document.file_size > 512000, UploadStates)
async def upload_file_too_big_handler(message: Message):
    await message.delete()
    await message.answer("❌ Файл слишком большой (> 500 КБ)")


>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
@router.message(F.document, UploadStates.pyrogram)
async def pyro_sqlite_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    with FileManager() as fm:
        await bot.download(message.document, fm.path)
        await message.delete()
        manager = await SessionManager.from_pyrogram_file(fm.path)

    await state.clear()
    session = await repo.session.add_from_manager(user.id, manager)

    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.message(F.text, UploadStates.pyrogram)
async def pyro_string_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    manager = SessionManager.from_pyrogram_string(message.text)
    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.message(F.document, UploadStates.telethon)
async def tele_sqlite_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    with FileManager(suffix=".session") as fm:
        await bot.download(message.document, fm.path)
        manager = await SessionManager.from_telethon_file(fm.path)

    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.message(F.text, UploadStates.telethon)
async def tele_string_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    manager = SessionManager.from_telethon_string(message.text)
    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.message(F.document, UploadStates.tdata)
async def tdata_handler(
    message: Message, state: FSMContext, bot: Bot, repo: Repo, user: User
):
    with FileManager(suffix=".zip") as fm:
        with FileManager() as fm2:
            await bot.download(message.document, fm2.path)
            with zipfile.ZipFile(fm2.path) as f:
                f.extractall(fm.path)

        if fm.path.joinpath("tdata").exists():
            tdata_path = fm.path.joinpath("tdata")
        else:
            tdata_path = fm.path

        manager = SessionManager.from_tdata_folder(tdata_path)

    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )


@router.message(F.document)
async def auto_handler(message: Message, bot: Bot):
    with FileManager() as fm:
        await bot.download(message.document, fm.path)
        session_type = await SessionManager.autodetect(fm.path)
    await message.copy_to(
        message.from_user.id,
        f"🔍 Автоопределение: <b>{session_type or 'Неизвестно'}</b>\n\nВыберите тип сессии:",
        reply_markup=kb.sessions.upload_auto(),
    )
    await message.delete()


@router.callback_query(F.data == "auto_pyrogram")
async def auto_pyrogram_handler(
    query: CallbackQuery, state: FSMContext, repo: Repo, user: User, bot: Bot
):
    with FileManager() as fm:
        await bot.download(query.message.document, fm.path)
        manager = await SessionManager.from_pyrogram_file(
            file=fm.path, filename=query.message.document.file_name.split(".")[0]
        )

    await state.clear()
    session = await repo.session.add_from_manager(user.id, manager)

    await query.message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
    await query.message.delete()


@router.callback_query(F.data == "auto_telethon")
async def auto_telethon_handler(
    query: CallbackQuery, state: FSMContext, repo: Repo, user: User, bot: Bot
):
    with FileManager() as fm:
        await bot.download(query.message.document, fm.path)
        manager = await SessionManager.from_telethon_file(fm.path)

    await state.clear()
    session = await repo.session.add_from_manager(user.id, manager)

    await query.message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
    await query.message.delete()


@router.callback_query(F.data == "auto_tdata")
async def auto_tdata_handler(
    query: CallbackQuery, state: FSMContext, repo: Repo, user: User, bot: Bot
):  
    with FileManager(suffix=".zip") as fm:
        with FileManager() as fm2:
            await bot.download(query.message.document, fm2.path)
            with zipfile.ZipFile(fm2.path) as f:
                f.extractall(fm.path)

        if fm.path.joinpath("tdata").exists():
            tdata_path = fm.path.joinpath("tdata")
        else:
            tdata_path = fm.path

        manager = SessionManager.from_tdata_folder(tdata_path)

    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await query.message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
    await query.message.delete()
    


=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
    )


>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
@router.message(F.text, UploadStates.manual_auth_key)
async def manual_auth_key_handler(message: Message, state: FSMContext):
    await state.update_data(auth_key=message.text)
    await state.set_state(UploadStates.manual_dc_id)
    await message.answer("Отправьте dc_id:")


@router.message(F.text.isdigit(), UploadStates.manual_dc_id)
async def manual_dc_id_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    if int(message.text) not in range(1, 5):
        await message.answer("❌ Неверный dc_id")
        return

    await state.update_data(dc_id=int(message.text))
    await state.set_state(UploadStates.manual_user_id)
    await message.answer("Отправьте user_id:", reply_markup=kb.sessions.skip())


@router.message(F.text.isdigit(), UploadStates.manual_user_id)
async def manual_user_id_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    user_id = int(message.text)

    data = await state.get_data()
    manager = SessionManager(
        auth_key=bytes.fromhex(data["auth_key"]),
        dc_id=data["dc_id"],
        user_id=user_id,
    )

    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await message.answer(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )


@router.callback_query(F.data == "skip", UploadStates.manual_user_id)
<<<<<<< HEAD
async def skip_user_id_handler(
    query: CallbackQuery, state: FSMContext, repo: Repo, user: User
):
=======
async def skip_user_id_handler(query: CallbackQuery, state: FSMContext, repo: Repo, user: User):
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    data = await state.get_data()
    manager = SessionManager(
        auth_key=bytes.fromhex(data["auth_key"]),
        dc_id=data["dc_id"],
    )

    session = await repo.session.add_from_manager(user.id, manager)

    await state.clear()
    await query.message.edit_text(
<<<<<<< HEAD
        text_session(manager), reply_markup=kb.sessions.action(session.id)
=======
        text_session(manager),
        reply_markup=kb.sessions.action(session.id)
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
    )
