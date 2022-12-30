from uuid import UUID
from functools import partial

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.misc.cd_data import SessionCb


def search():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Искать", switch_inline_query_current_chat="")
    return builder.as_markup()


def auth_type():
    builder = InlineKeyboardBuilder()
    builder.button(text="☎️ Телефон", callback_data="login_phone")
    # builder.button(text="📱 QR-код", callback_data="login_qr")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)

    return builder.as_markup()


def phone_confirm():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Нет", callback_data="phone_cancel")
    builder.button(text="✅ Да", callback_data="phone_confirm")

    return builder.as_markup()


def upload():
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄️ Pyrogram", callback_data="upload_pyrogram")
    builder.button(text="🔄️ Telethon", callback_data="upload_telethon")
    builder.button(text="🔄️ TData ZIP", callback_data="upload_tdata")
    builder.button(text="✍️ Manual", callback_data="upload_manual")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)

    return builder.as_markup()


def upload_auto():
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄️ Pyrogram", callback_data="auto_pyrogram")
    builder.button(text="🔄️ Telethon", callback_data="auto_telethon")
    builder.button(text="🔄️ TData ZIP", callback_data="auto_tdata")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2)

    return builder.as_markup()


def action(session_id: UUID):
    builder = InlineKeyboardBuilder()
    Cb = partial(SessionCb, session_id=session_id)

    builder.button(text="🔎 Validate", callback_data=Cb(action="validate"))
    builder.button(text="🔑 Auth key", callback_data=Cb(action="auth_key"))
    builder.button(text="🔄️ Pyro session", callback_data=Cb(action="pyro_sql"))
    builder.button(text="🔄️ Pyro string", callback_data=Cb(action="pyro_str"))
    builder.button(text="🔄️ Tele session", callback_data=Cb(action="tele_sql"))
    builder.button(text="🔄️ Tele string", callback_data=Cb(action="tele_str"))
    builder.button(text="🔄️ TData ZIP", callback_data=Cb(action="tdata_zip"))
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(2, 2, 2, 1, 1)

    return builder.as_markup()


def back_to_session(session_id: UUID):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⬅️ Back",
        callback_data=SessionCb(session_id=session_id, action="back")
    )

    return builder.as_markup()


def skip():
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭️ Пропустить", callback_data="skip")
    return builder.as_markup()
