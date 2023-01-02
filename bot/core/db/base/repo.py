from typing import Any

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import EMPTY_DICT


class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _session_add(self, *instances) -> None:
        self._session.add_all(instances)

    async def _execute(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Result:
        return await self._session.execute(
            statement, params, execution_options, bind_arguments, **kw
        )

    async def _scalar(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Any:
        result = await self._execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalar()

    async def _scalar_one(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Any:
        result = await self._execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalar_one()

    async def _scalars_all(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> list[Any]:
        result = await self._execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalars().all()

    async def commit(self, *instances) -> None:
        if instances:
            self._session_add(*instances)

        await self._session.commit()
