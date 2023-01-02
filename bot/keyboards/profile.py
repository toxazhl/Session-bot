from aiogram.utils.keyboard import InlineKeyboardBuilder


def profile():
    builder = InlineKeyboardBuilder()

    builder.button(text="🔍 Мои сессии", switch_inline_query_current_chat="")
    builder.button(text="💳 Пополнить баланс", callback_data="refill_balance")

    return builder.as_markup()


def pay_url(url: str):
    builder = InlineKeyboardBuilder()

    builder.button(text="💳 Оплатить", url=url)

    return builder.as_markup()
