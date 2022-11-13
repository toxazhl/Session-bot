from aiogram.utils.keyboard import InlineKeyboardBuilder


def choose():
    builder = InlineKeyboardBuilder()

    builder.button(text="Pyrogram", callback_data="pyrogram")
    builder.button(text="Telethon", callback_data="telethon")
    builder.button(text="TData", callback_data="tdata")
    builder.button(text="tgnet.dat", callback_data="tgnet.dat")

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
