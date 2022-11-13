import secrets
from pathlib import Path


class BaseSession:
    SESSION_PATH = Path.cwd() / "sessions"

    def __init__(self, name: None | str = None):
        self.name = name or self.new_name()

    @staticmethod
    def new_name() -> str:
        return secrets.token_urlsafe(8)
