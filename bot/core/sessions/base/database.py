from typing import TYPE_CHECKING

import aiosqlite

if TYPE_CHECKING:
    from pathlib import Path


class BaseDatabase:
    def __init__(self, path: "Path", schema=None):
        self.path = path
        self.schema = schema

    async def __aenter__(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        if self.schema:
            await self.conn.executescript(self.schema)
            await self.conn.commit()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()
