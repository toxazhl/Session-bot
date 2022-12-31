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

from bot import keyboards as kb
from bot.core.db import Repo
from bot.core.session.proxy import ProxyManager
from bot.core.session.session import SessionManager
from bot.misc.cd_data import SessionCb
from bot.utils.gen_text import text_session

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "📝 История")
async def tele_string_handler(message: Message):
    await message.answer(
        "🔽 Нажми на кнопку что-бы посмотреть ранее созданные или загруженные сессии\n"
        "🔍 Также ты можешь искать сессии по номеру, имени, юзернейму или ID",
        reply_markup=kb.sessions.search(),
    )


@router.message(F.via_bot)
async def tele_string_handler(message: Message, repo: Repo):
    session = await repo.session.get(message.text)
    manager = SessionManager.from_session(session)

    await message.answer(
        text_session(manager), reply_markup=kb.sessions.action(session.id)
    )


@router.inline_query()
async def show_user_links(inline_query: InlineQuery, repo: Repo):
    offset = int(inline_query.offset) if inline_query.offset else 0
    sessions = await repo.session.get_all(
        inline_query.from_user.id, offset, query=inline_query.query
    )
    results = []
    for session in sessions:
        if session.first_name:
            title = session.first_name + " " + (session.last_name or "")
        else:
            title = session.telegram_id or session.id

        description = str(session.telegram_id)
        if session.phone:
            description += f"\n{session.phone}"
        if session.username:
            description += f" @{session.username}"

        results.append(
            InlineQueryResultArticle(
                id=str(session.id),  # ссылки у нас уникальные, потому проблем не будет
                title=str(title),
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
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo)

    await query.message.edit_text(
        text_session(manager), reply_markup=kb.sessions.action(session_id)
    )


@router.callback_query(SessionCb.filter(F.action == "validate"))
async def validate_handler(
    query: CallbackQuery, callback_data: SessionCb, repo: Repo, pm: ProxyManager
):
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo, pm.get)
    await manager.validate()
    await repo.session.update(session_id, manager)
    await query.answer()
    try:
        await query.message.edit_text(
            text_session(manager), reply_markup=kb.sessions.action(session_id)
        )
    except TelegramBadRequest:
        pass


@router.callback_query(SessionCb.filter(F.action == "auth_key"))
async def auth_key_handler(query: CallbackQuery, callback_data: SessionCb, repo: Repo):
    session_id = callback_data.session_id
    manager = await SessionManager.from_database(session_id, repo)
    await query.message.edit_text(
        hcode(manager.auth_key_hex),
        reply_markup=kb.sessions.back_to_session(session_id),
    )
