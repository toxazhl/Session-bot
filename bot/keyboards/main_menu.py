from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def menu():
    builder = ReplyKeyboardBuilder()

    builder.button(text="🆕 Войти")
    builder.button(text="⬆️ Загрузить")
    # builder.button(text="📝 История")
    builder.button(text="👤 Профиль")

    builder.adjust(2, 1)

    return builder.as_markup(resize_keyboard=True)


def close():
    builder = InlineKeyboardBuilder()

    builder.button(text="❌ Закрыть", callback_data="close")

    return builder.as_markup(resize_keyboard=True)
