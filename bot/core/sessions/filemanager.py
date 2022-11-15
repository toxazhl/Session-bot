import secrets
import shutil
from pathlib import Path


class FileManager:
    BASE_PATH = Path.cwd() / "sessions"

    def __init__(
        self,
        base_path: None | str | Path = None,
        ext: str = "",
    ):
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = self.BASE_PATH

        self.base_path.mkdir(parents=True, exist_ok=True)

        self.extension = ext
        self.path = self.BASE_PATH / self.token_hex()
        if self.extension:
            self.path = self.path.with_suffix(self.extension)

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
