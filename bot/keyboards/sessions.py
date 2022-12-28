from uuid import UUID
from functools import partial

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.misc.cd_data import SessionCb


def upload():
    builder = InlineKeyboardBuilder()

    builder.button(text="🔄️ Pyrogram", callback_data="upload_pyrogram")
    builder.button(text="🔄️ Telethon", callback_data="upload_telethon")
    builder.button(text="🔄️ TData ZIP", callback_data="upload_tdata")
    builder.button(text="✍️ Manual", callback_data="upload_manual")
    builder.button(text="🆕 Создать", callback_data="upload_create")

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

    builder.adjust(2)

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
