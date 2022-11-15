from pathlib import Path

from bot.core.sessions.base.database import BaseDatabase


SCHEMA = """
CREATE TABLE version (version integer primary key);

CREATE TABLE sessions (
    dc_id integer primary key,
    server_address text,
    port integer,
    auth_key blob,
    takeout_id integer
);

CREATE TABLE entities (
    id integer primary key,
    hash integer not null,
    username text,
    phone integer,
    name text,
    date integer
);

CREATE TABLE sent_files (
    md5_digest blob,
    file_size integer,
    type integer,
    id integer,
    hash integer,
    primary key(md5_digest, file_size, type)
);

CREATE TABLE update_state (
    id integer primary key,
    pts integer,
    qts integer,
    date integer,
    seq integer
);
"""


class Database(BaseDatabase):
    def __init__(self, path: str | Path, create: bool = False):
        if create:
            super().__init__(path, SCHEMA)
        else:
            super().__init__(path)

    async def get_session(self) -> dict[str, int | str | bytes]:
        async with self.conn.execute("SELECT * FROM sessions") as cursor:
            row = await cursor.fetchone()

        return {key: row[key] for key in row.keys()}

    async def add_session(
        self,
        dc_id: int,
        auth_key: bytes,
        server_address: None | str = None,
        port: None | int = None,
        takeout_id: None | bool = None,
    ):
        await self.conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            (dc_id, server_address, port, auth_key, takeout_id),
        )
        await self.conn.commit()
