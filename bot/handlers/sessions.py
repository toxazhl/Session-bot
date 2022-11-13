import logging

import opentele
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import keyboards as kb
from bot.core.db import Repo

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🪪 Сессії")
async def sessions_handler(message: Message, state: FSMContext, repo: Repo):
    return await start_handler(message, state)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    return message.answer(
        "Ви в головному меню ⚡\n"
        "Оберіть дію:",
        reply_markup=kb.main_menu.menu()
    )
