import secrets
import shutil
from pathlib import Path


class FileManager:
    BASE_PATH = Path.cwd() / "sessions"

    def __init__(
        self,
        base_path: None | str | Path = None,
        suffix: str = "",
    ):
        base_path = Path(base_path) if base_path else self.BASE_PATH
        base_path.mkdir(parents=True, exist_ok=True)
        self.path = base_path / self.token_hex()

        if suffix:
            self.path = self.path.with_suffix(suffix)

        self.name = self.path.name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path and self.path.exists():
            if self.path.is_dir():
                shutil.rmtree(self.path)
            else:
                self.path.unlink()

    def token_hex(self):
        return secrets.token_urlsafe(4)

    def zip(self, path: Path):
        shutil.make_archive(path.with_suffix(""), "zip", self.path)
