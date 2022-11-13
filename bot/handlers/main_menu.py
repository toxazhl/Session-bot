import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import keyboards as kb
from bot.core.db import Repo
from bot.filters.user import NewUserFilter

logger = logging.getLogger(__name__)

router = Router()


@router.message(NewUserFilter())
async def new_user_handler(message: Message, state: FSMContext, repo: Repo):
    await repo.user.add(id=message.from_user.id)
    return await start_handler(message, state)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    return message.answer(
        "Ви в головному меню ⚡\n"
        "Оберіть дію:",
        reply_markup=kb.main_menu.menu()
    )
