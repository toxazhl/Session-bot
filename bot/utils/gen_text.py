from aiogram.utils.markdown import hcode, hlink
from pyrogram.enums.user_status import UserStatus

from bot.core.session.session import SessionManager


def text_session(manager: SessionManager) -> str:
    if manager.source:
        t = f"📂 Session [{manager.source.name}]\n\n"  # text
    else:
        t = "📂 Session\n\n"  # text

    user = manager.user
    link = "tg://user?id="
    valid = "?" if manager.valid is None else ("❌", "✅")[manager.valid]

    t += f"💾 DC ID: {hcode(manager.dc_id)}\n"
    t += f"☑️ Valid: {hcode(valid)}\n"

    if manager.user_id:
        t += "🪪 User:\n"
        if manager.first_name:
            t += f'├─👤 Name: {hlink(manager.first_name, f"{link}{manager.user_id}")}\n'
        t += f"├─📧 Username: @{manager.username}\n" if manager.username else ""
        t += f"├─☎️ Phone: <code>{manager.phone}</code>\n" if manager.phone else ""

        if user:
            status = ""
            if user.status == UserStatus.ONLINE:
                status = "🟢 Online"
            elif user.status == UserStatus.RECENTLY:
                status = "🟡 Recently"
            elif user.status == UserStatus.OFFLINE and user.last_online_date:
                status = f"🔴 {user.last_online_date:%Y.%m.%d %H:%M:%S}"

            t += f"├─📶 Status: {status}\n" if status else ""

        if manager.user_id:
            t += f'└─🆔 ID: {hlink(str(manager.user_id), f"{link}{manager.user_id}")}'

    return t
