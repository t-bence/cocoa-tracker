import os
from typing import override
from src.common.storage import Storage


class LocalStorage(Storage):
    """Local-filesystem backend - useful for unit tests."""

    def __init__(self, base_dir: str = "."):
        self._base_dir = base_dir

    def _path(self, key: str) -> str:
        return os.path.join(self._base_dir, key)

    @override
    def read(self, key: str) -> bytes | None:
        path = self._path(key)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    @override
    def write(self, key: str, data: bytes) -> None:
        path = self._path(key)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
