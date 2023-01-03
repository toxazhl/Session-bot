import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards as kb
from bot.core.db.repo import Repo
from bot.filters.user import NewUserFilter

logger = logging.getLogger(__name__)

router = Router()


@router.message(NewUserFilter())
async def new_user_handler(message: Message, state: FSMContext, repo: Repo):
    await repo.user.add(id=message.from_user.id)
    await start_handler(message, state)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет 👋\n"
        "🤖 Этот бот может конвертировать и создавать новые Telegram сессии\n\n"
        "🥇 Возможности:\n"
        "✅ Конвертирование сессий между Pyrogram, Telethon и TData\n"
        "✅ Создание новых сессий в любом формате\n"
        "✅ Быстрый вход в чужой Telegram для слежки",
        reply_markup=kb.main_menu.menu(),
    )


@router.callback_query(F.data == "close")
async def upload_pyrogram_handler(query: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await query.message.delete()
    except TelegramBadRequest:
        pass
