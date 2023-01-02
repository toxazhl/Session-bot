import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot.core.db.models import User
from bot.core.db.repo import Repo
from bot.core.payment.crystalpay import CrystalPay
from bot.misc.states import ProfileStates

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "👤 Профиль")
async def upload_session_handler(
    message: Message, user: User, repo: Repo, state: FSMContext
):
    await state.clear()
    session_count = await repo.session.count(user_id=message.from_user.id)
    await message.answer(
        "👤 Ваш профиль\n"
        f"💰 Баланс: {user.balance / 100:.2f}$\n"
        f"📂 Количество сессий: {session_count}\n",
        reply_markup=kb.profile.profile(),
    )


@router.callback_query(F.data == "refill_balance")
async def refill_balance_handler(query: CallbackQuery, state: FSMContext):
    await query.answer("❌ Временно не доступно")
    # await query.message.edit_text("💰 Введите сумму пополнения:\n(Минимум 5$)")
    # await state.set_state(ProfileStates.refill_amount)


@router.message(F.text.isdigit(), ProfileStates.refill_amount)
async def amount_handler(message: Message, bot: Bot, crystalpay: CrystalPay):
    amount = int(message.text)
    if amount < 5:
        return await message.answer(
            "Минимальная сумма пополнения 5$\nПопробуй еще раз:"
        )

    invoice = await crystalpay.invoice_create(
        amount=amount,
        currency="USD",
        lifetime=1440,
        extra=str(message.from_user.id),
        redirect=f"https://t.me/{(await bot.me()).username}",
    )
    if invoice["error"]:
        return await message.answer(
            "При создании инвойса произошла ошибка, обратись к администратору"
        )

    await message.answer(
        "Инвойс оплаты создан 👇", reply_markup=kb.profile.pay_url(invoice["url"])
    )
