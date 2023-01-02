import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot.core.db.models import User
from bot.core.db.repo import Repo
from bot.core.session.enums import SessionSource
from bot.core.session.files import FileManager
from bot.core.session.session import SessionManager
from bot.misc.states import UploadStates

from .menu import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "⬆️ Загрузить")
async def upload_session_handler(message: Message, state: FSMContext):
    await state.set_state(UploadStates.upload)
    await message.answer(
        "Отправь файл или строку сессии в любом формате",
        reply_markup=kb.sessions.upload(),
    )


@router.callback_query(F.data == "upload_manual")
async def upload_manual_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(UploadStates.manual_auth_key)
    await query.message.edit_text("🗝️ Отправь auth_key в HEX формате:")


@router.message(F.document.file_size > 15360000)
async def upload_file_too_big_handler(message: Message):
    await message.reply(
        "❌ Файл слишком большой (> 15 МБ), попробуй очистить его\n"
        "Если это сессия Pyrogram - очисти таблицу <code>peers</code>\n"
        "Если это сессия Telethon - очисти таблицу <code>entities</code>\n"
        "Если это архив с TData - убедись что там нету самого приложения Telegram и очисти кеш"
    )


@router.message(F.text, UploadStates.upload)
async def auto_string_handler(message: Message, state: FSMContext, repo: Repo):
    manager = SessionManager.autoimport_string(message.text)
    await post_autoimport(manager, message, state, repo)


@router.message(F.document)
async def auto_handler(message: Message, state: FSMContext, repo: Repo, bot: Bot):
    with FileManager() as fm:
        await bot.download(message.document, fm.path)
        manager = await SessionManager.autoimport(fm.path)
    await post_autoimport(manager, message, state, repo)


async def post_autoimport(
    manager: SessionManager, message: Message, state: FSMContext, repo: Repo
):
    if not manager:
        await message.reply("❌ Не удалось определить тип сессии")
        return None

    await state.clear()
    session = await repo.session.add_from_manager(message.from_user.id, manager)
    await message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
    await message.delete()


@router.message(F.text, UploadStates.manual_auth_key)
async def manual_auth_key_handler(message: Message, state: FSMContext):
    await state.update_data(auth_key=message.text)
    await state.set_state(UploadStates.manual_dc_id)
    await message.answer("💾 Отправьте dc_id:")


@router.message(F.text.isdigit(), UploadStates.manual_dc_id)
async def manual_dc_id_handler(message: Message, state: FSMContext):
    if int(message.text) not in range(1, 5):
        await message.answer("❌ Неверный dc_id")
        return

    await state.update_data(dc_id=int(message.text))
    await state.set_state(UploadStates.manual_user_id)
    await message.answer("🆔 Отправьте user_id:", reply_markup=kb.sessions.skip())


@router.message(F.text.isdigit(), UploadStates.manual_user_id)
async def manual_user_id_handler(
    message: Message, state: FSMContext, repo: Repo, user: User
):
    data = await state.get_data()
    data["user_id"] = int(message.text)
    await post_manual(data, message, state, repo)


@router.callback_query(F.data == "skip", UploadStates.manual_user_id)
async def skip_user_id_handler(query: CallbackQuery, state: FSMContext, repo: Repo):
    data = await state.get_data()
    await post_manual(data, query.message, state, repo)


async def post_manual(data: dict, message: Message, state: FSMContext, repo: Repo):
    manager = SessionManager(
        auth_key=bytes.fromhex(data["auth_key"]),
        dc_id=data["dc_id"],
        user_id=data.get("user_id"),
        source=SessionSource.MANUAL,
    )
    session = await repo.session.add_from_manager(user.id, manager)
    await state.clear()
    await message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
