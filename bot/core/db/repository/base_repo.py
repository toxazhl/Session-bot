from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.util import EMPTY_DICT


class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def session_add(self, *instances) -> None:
        self.session.add_all(instances)

    async def execute(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Result:
        return await self.session.execute(
            statement, params, execution_options, bind_arguments, **kw
        )

    async def scalar(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Any:
        result = await self.execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalar()

    async def scalar_one(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> Any:
        result = await self.execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalar_one()

    async def scalars_all(
        self,
        statement,
        params=None,
        execution_options=EMPTY_DICT,
        bind_arguments=None,
        **kw
    ) -> list[Any]:
        result = await self.execute(
            statement,
            params=params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            **kw
        )
        return result.scalars().all()

    async def commit(self, *instances) -> None:
        if instances:
            self.session_add(*instances)

        await self.session.commit()
