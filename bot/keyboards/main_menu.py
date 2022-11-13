from aiogram.utils.keyboard import ReplyKeyboardBuilder


def menu():
    builder = ReplyKeyboardBuilder()

    builder.button(text="🪪 Сессії")
    builder.button(text="👤 Профіль")

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
