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
        server_address: str,
        port: int,
        telegram_id: None | int = None,
        api_id: None | int = None,
        test_mode: None | bool = None,
        is_bot: None | bool = None,
        valid: None | bool = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            auth_key=auth_key,
            api_id=api_id,
            dc_id=dc_id,
            server_address=server_address,
            port=port,
            telegram_id=telegram_id,
            test_mode=test_mode,
            is_bot=is_bot,
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
            api_id=manager.api_id,
            server_address=manager.server_address,
            port=manager.port,
            telegram_id=manager.user_id,
            is_bot=manager.is_bot,
            test_mode=manager.test_mode,
            valid=manager.valid,
        )

    async def update(
        self, session_id: "UUID", valid: None | bool = None
    ) -> None:
        stmt = (
            update(Session).
            where(Session.id == session_id).
            values(valid=valid)
        )
        await self.execute(stmt)
        await self.commit()

    async def get(self, id: "UUID") -> Session:
        stmt = select(Session).where(Session.id == id)
        return await self.scalar(stmt)
