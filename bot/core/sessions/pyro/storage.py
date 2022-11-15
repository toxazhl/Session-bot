from typing import TYPE_CHECKING

from bot.core.sessions.base.database import BaseDatabase

if TYPE_CHECKING:
    from pathlib import Path


SCHEMA = """
CREATE TABLE sessions (
    dc_id     INTEGER PRIMARY KEY,
    api_id    INTEGER,
    test_mode INTEGER,
    auth_key  BLOB,
    date      INTEGER NOT NULL,
    user_id   INTEGER,
    is_bot    INTEGER
);

CREATE TABLE peers (
    id             INTEGER PRIMARY KEY,
    access_hash    INTEGER,
    type           INTEGER NOT NULL,
    username       TEXT,
    phone_number   TEXT,
    last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER))
);

CREATE TABLE version (
    number INTEGER PRIMARY KEY
);

CREATE INDEX idx_peers_id ON peers (id);
CREATE INDEX idx_peers_username ON peers (username);
CREATE INDEX idx_peers_phone_number ON peers (phone_number);

CREATE TRIGGER trg_peers_last_update_on
    AFTER UPDATE
    ON peers
BEGIN
    UPDATE peers
    SET last_update_on = CAST(STRFTIME('%s', 'now') AS INTEGER)
    WHERE id = NEW.id;
END;
"""


class Database(BaseDatabase):
    def __init__(self, path: "Path", create: bool = False):
        if create:
            super().__init__(path, SCHEMA)
        else:
            super().__init__(path)

    async def get_session(self) -> dict[str, int | bytes]:
        async with self.conn.execute("SELECT * FROM sessions") as cursor:
            row = await cursor.fetchone()

        return {key: row[key] for key in row.keys()}

    async def add_session(
        self,
        dc_id: int,
        auth_key: bytes,
        api_id: None | int = None,
        user_id: None | int = None,
        is_bot: None | bool = None,
        test_mode: None | bool = None
    ):
        await self.conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (dc_id, api_id, test_mode, auth_key, 0, user_id, is_bot)
        )
        await self.conn.commit()
