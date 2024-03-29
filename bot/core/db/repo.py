from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, or_, select, update

from bot.core.db.base.repo import BaseRepo
from bot.core.db.models import Proxy, Session, User
from bot.core.session.enums import SessionSource

if TYPE_CHECKING:
    from bot.core.session.session import SessionManager


class Repo(BaseRepo):
    async def add_user(self, id: int) -> None:
        user = User(id=id)
        await self.commit(user)

    async def get_user(self, id: int) -> User:
        stmt = select(User).where(User.id == id)
        return await self._scalar(stmt)

    async def add_session(
        self,
        user_id: int,
        dc_id: int,
        auth_key: bytes,
        telegram_id: None | int = None,
        valid: None | bool = None,
        first_name: None | str = None,
        last_name: None | str = None,
        username: None | str = None,
        phone: None | str = None,
        filename: None | str = None,
        source: None | SessionSource = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            auth_key=auth_key,
            dc_id=dc_id,
            telegram_id=telegram_id,
            valid=valid,
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=phone,
            filename=filename,
            source=source,
        )
        await self.commit(session)
        return session

    async def add_session_from_manager(
        self, user_id: int, manager: "SessionManager"
    ) -> Session:
        return await self.add_session(
            user_id=user_id,
            dc_id=manager.dc_id,
            auth_key=manager.auth_key,
            telegram_id=manager.user_id,
            valid=manager.valid,
            first_name=manager.first_name,
            last_name=manager.last_name,
            username=manager.username,
            phone=manager.phone,
            filename=manager.filename,
            source=manager.source,
        )

    async def update_session(self, session_id: UUID, manager: "SessionManager") -> None:
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
        await self._execute(stmt)
        await self.commit()

    async def get_session(self, id: UUID) -> Session:
        stmt = select(Session).where(Session.id == id)
        return await self._scalar_one(stmt)

    async def search_session(
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
            .where(Session.user_id == user_id)
            .where(or_(*conds))
            .offset(offset)
            .limit(limit)
            .order_by(Session.creation_date.desc())
        )

        return await self._scalars_all(stmt)

    async def count_sessions(self, user_id: None | int = None) -> int:
        stmt = select(func.count(Session.id))
        if user_id:
            stmt = stmt.where(Session.user_id == user_id)

        return await self._scalar(stmt)

    async def get_all_proxies(self) -> list[Proxy]:
        stmt = select(Proxy)
        return await self._scalars_all(stmt)
