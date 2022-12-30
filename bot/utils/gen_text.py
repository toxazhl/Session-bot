from aiogram.utils.markdown import hcode, hlink
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently

from bot.core.sessions.manager import SessionManager


def text_session(manager: SessionManager) -> str:
    t = "📂 Session\n\n"  # text

    user = manager.user
    link = "tg://user?id="
    valid = "?" if manager.valid is None else ("❌", "✅")[manager.valid]

    t += f"💾 DC ID: {hcode(manager.dc_id)}\n"
    t += f"☑️ Valid: {hcode(valid)}\n"
    t += f"🪪 User:\n"
    if manager.first_name:
        t += f'├─👤 Name: {hlink(manager.first_name, f"{link}{manager.user_id}")}\n'
    t += f"├─📧 Username: @{manager.username}\n" if manager.username else ""
    t += f"├─☎️ Phone: <code>{manager.phone}</code>\n" if manager.phone else ""

    if user and user.status:
        status = ""
        if isinstance(user.status, UserStatusOnline):
            status = "🟢 Online"
        elif isinstance(user.status, UserStatusRecently):
            status = "🟡 Recently"
        elif isinstance(user.status, UserStatusOffline) and user.status.was_online:
            status = f"🔴 {user.status.was_online:%Y.%m.%d %H:%M:%S}"

        t += f"├─📶 Status: {status}\n" if status else ""

    if manager.user_id:
        t += f'└─🆔 ID: {hlink(str(manager.user_id), f"{link}{manager.user_id}")}'

    return t
