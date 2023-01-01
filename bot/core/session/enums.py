from enum import Enum, auto


class SessionSource(Enum):
    TELETHON_FILE = auto()
    """Telethon file .session"""

    TELETHON_STRING = auto()
    """Telethon string session"""

    PYROGRAM_FILE = auto()
    """Pyrogram file .session"""

    PYROGRAM_STRING = auto()
    """Pyrogram string session"""

    LOGIN_PHONE = auto()
    """Login by phone"""

    TDATA = auto()
    """Tdata session"""

    MANUAL = auto()
    """Manual create"""

    def __repr__(self):
        return f"{self}"
