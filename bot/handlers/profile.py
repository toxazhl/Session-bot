import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot.core.db.models import User
from bot.core.db.repo import Repo

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "👤 Профиль")
async def upload_session_handler(
    message: Message, user: User, repo: Repo, state: FSMContext
):
    await state.clear()
    session_count = await repo.count_sessions(user_id=message.from_user.id)
    await message.answer(
        "👤 Ваш профиль\n"
        f"💰 Баланс: {user.balance / 100:.2f}$\n"
        f"📂 Количество сессий: {session_count}\n",
        reply_markup=kb.profile.profile(),
    )


@router.callback_query(F.data == "refill_balance")
async def refill_balance_handler(query: CallbackQuery):
    await query.answer("❌ Временно не доступно")
