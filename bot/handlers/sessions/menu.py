import logging
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hlink
from telethon.tl.types import (
    UserStatusOnline, UserStatusOffline, UserStatusRecently
)

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.sessions.manager import SessionManager
from bot.misc.cd_data import SessionCb


logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(SessionCb.filter(F.action == "back"))
async def show_session(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo)

    return query.message.edit_text(
        text_session(manager),
        reply_markup=kb.sessions.action(session_id)
    )


@router.callback_query(SessionCb.filter(F.action == "validate"))
async def validate_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo)

    if await manager.validate():
        await query.answer("✅ Сессия валидна", show_alert=True)
    else:
        await query.answer("❌ Сессия не валидна", show_alert=True)

    await repo.session.update(session_id, manager)

    return query.message.edit_text(
        text_session(manager),
        reply_markup=kb.sessions.action(session_id)
    )


@router.callback_query(SessionCb.filter(F.action == "auth_key"))
async def auth_key_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo
):
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo)
    return query.message.edit_text(
        hcode(manager.auth_key_hex),
        reply_markup=kb.sessions.back_to_session(session_id)
    )


def text_session(manager: SessionManager) -> str:
    t = "📂 Session\n\n"

    auth_key = f"{manager.auth_key_hex[:8]}...{manager.auth_key_hex[-8:]}"
    user = manager.user
    link = "tg://user?id="
    valid = "?" if manager.valid is None else ("❌", "✅")[manager.valid]

    t += (
        f"🆔 DC ID: {hcode(manager.dc_id)}\n"
        f"🔑 Auth Key: {hcode(auth_key)}\n"
        f"🆗  Valid: {hcode(valid)}\n"
    )

    if user:
        status = ""
        if status := user.status:
            if isinstance(status, UserStatusOnline):
                status = "🟢 Online"
            elif isinstance(status, UserStatusRecently):
                status = "🟡 Recently"
            elif isinstance(status, UserStatusOffline) and status.was_online:
                status = f"🔴 {status.was_online:%Y.%m.%d %H:%M:%S}"

        t += "👤 User: \n"
        t += f'├─👤 Name: {hlink(user.first_name, f"{link}{user.id}")}\n'
        t += f"├─💻 Username: @{user.username}\n" if user.username else ""
        t += f"├─📞 Phone: <code>{user.phone}</code>\n" if user.phone else ""
        t += f"├─📶 Status: {status}\n" if status else ""
        t += f"└─🆔 ID: <code>{user.id}</code>\n"

    elif manager.user_id:
        t += f'🆔 ID: {hlink(str(manager.user_id), f"{link}{manager.user_id}")}'

    return t
