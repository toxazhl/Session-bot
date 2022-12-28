from typing import TYPE_CHECKING

from sqlalchemy import select, update

from bot.core.db.models import Session
from .base_repo import BaseRepo

if TYPE_CHECKING:
    from uuid import UUID
    from bot.core.sessions.manager import SessionManager


class SessionRepo(BaseRepo):
    async def add(
        self,
        user_id: int,
        dc_id: int,
        auth_key: bytes,
        telegram_id: None | int = None,
        valid: None | bool = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            auth_key=auth_key,
            dc_id=dc_id,
            telegram_id=telegram_id,
            valid=valid
        )
        await self.commit(session)
        return session

    async def add_from_manager(
        self, user_id: int, manager: "SessionManager"
    ) -> Session:
        return await self.add(
            user_id=user_id,
            dc_id=manager.dc_id,
            auth_key=manager.auth_key,
            telegram_id=manager.user_id,
            valid=manager.valid,
        )

    async def update(
        self, session_id: "UUID", manager: "SessionManager"
    ) -> None:
        stmt = (
            update(Session).
            where(Session.id == session_id).
            values(valid=manager.valid, telegram_id=manager.user_id)
        )
        await self.execute(stmt)
        await self.commit()

    async def get(self, id: "UUID") -> Session:
        stmt = select(Session).where(Session.id == id)
        return await self.scalar(stmt)
