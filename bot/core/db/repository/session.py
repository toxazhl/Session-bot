from typing import TYPE_CHECKING

from sqlalchemy import select, update, or_

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
        filename: None | str = None
    ) -> Session:
        session = Session(
            user_id=user_id,
            auth_key=auth_key,
            dc_id=dc_id,
            telegram_id=telegram_id,
            valid=valid,
            filename=filename
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
            filename=manager.filename
        )

    async def update(self, session_id: "UUID", manager: "SessionManager") -> None:
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(
                valid=manager.valid,
                telegram_id=manager.user_id,
                first_name=manager.first_name,
                last_name=manager.last_name,
                username=manager.username,
                phone=manager.phone,
            )
        )
        await self.execute(stmt)
        await self.commit()

    async def get(self, id: "UUID") -> Session:
        stmt = select(Session).where(Session.id == id)
        return await self.scalar(stmt)

    async def get_all(
        self, user_id: int, offset: int = 0, limit: int = 50, query: None | str = None
    ) -> list[Session]:
        search_columns = (
            Session.first_name,
            Session.last_name,
            Session.username,
            Session.phone,
        )
        conds = []
        if query:
            conds += [column.contains(query) for column in search_columns]
            if query.isdigit():
                conds.append(Session.telegram_id == int(query))

        stmt = (
            select(Session)
            .where(Session.user_id == user_id).where(or_(*conds))
            .offset(offset)
            .limit(limit)
            .order_by(Session.creation_date.desc())
        )

        return await self.scalars_all(stmt)
