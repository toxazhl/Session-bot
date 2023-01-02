import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiogram.utils.markdown import hcode
from opentele.api import API

from bot import keyboards as kb
from bot.core.db.repo import Repo
from bot.core.session.client import ClientManager
from bot.core.session.session import SessionManager
from bot.misc.cd_data import SessionCb
from bot.utils.gen_text import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "📝 История")
async def history_handler(message: Message):
    await message.answer(
        "🔽 Нажми на кнопку что-бы посмотреть ранее созданные или загруженные сессии\n"
        "🔍 Также ты можешь искать сессии по номеру, имени, юзернейму или ID",
        reply_markup=kb.sessions.search(),
    )


@router.message(F.via_bot)
async def session_handler(message: Message, repo: Repo):
    session = await repo.session.get(message.text)
    manager = SessionManager.from_session(session)

    await message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )


@router.inline_query()
async def show_user_links(inline_query: InlineQuery, repo: Repo):
    offset = int(inline_query.offset) if inline_query.offset else 0
    sessions = await repo.session.search(
        inline_query.from_user.id, offset, query=inline_query.query
    )
    results = []
    for session in sessions:
        if session.first_name:
            title = session.first_name + " " + (session.last_name or "")
        else:
            title = session.telegram_id or str(session.id)

        description = str(session.telegram_id)
        if session.phone:
            description += f"\n{session.phone}"
        if session.username:
            description += f" @{session.username}"

        results.append(
            InlineQueryResultArticle(
                id=str(session.id),
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=str(session.id),
                ),
            )
        )

    await inline_query.answer(
        results, is_personal=True, next_offset=str(offset + 50), cache_time=10
    )


@router.callback_query(SessionCb.filter(F.action == "back"))
async def show_session(query: CallbackQuery, callback_data: SessionCb, repo: Repo):
    manager = await SessionManager.from_database(callback_data.session_id, repo)

    await query.message.edit_text(
        text_session(manager), reply_markup=kb.sessions.action(callback_data.session_id)
    )


@router.callback_query(SessionCb.filter(F.action == "validate"))
async def validate_handler(
    query: CallbackQuery,
    callback_data: SessionCb,
    repo: Repo,
    client_manager: ClientManager,
):
    manager = await SessionManager.from_database(callback_data.session_id, repo)
    api = API.TelegramDesktop.Generate(system="windows")
    await manager.validate(client_manager, api)

    await repo.session.update(callback_data.session_id, manager)
    try:
        await query.answer("✅ Валид" if manager.valid else "❌ Не валид")
    except TelegramBadRequest:
        pass

    try:
        await query.message.edit_text(
            text_session(manager),
            reply_markup=kb.sessions.action(callback_data.session_id),
        )
    except TelegramBadRequest:
        pass


@router.callback_query(SessionCb.filter(F.action == "auth_key"))
async def auth_key_handler(query: CallbackQuery, callback_data: SessionCb, repo: Repo):
    manager = await SessionManager.from_database(callback_data.session_id, repo)
    await query.message.edit_text(
        hcode(manager.auth_key_hex),
        reply_markup=kb.sessions.back_to_session(callback_data.session_id),
    )
