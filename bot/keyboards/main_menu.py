from aiogram.utils.keyboard import ReplyKeyboardBuilder


def menu():
    builder = ReplyKeyboardBuilder()

    builder.button(text="📤 Загрузить сессию")
    builder.button(text="👤 Профиль")

    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
