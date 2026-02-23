import datetime as dt
import json
import os
from abc import ABC, abstractmethod

# ---------------------------------------------------------------------------
# Abstract storage backend
# ---------------------------------------------------------------------------


class Storage(ABC):
    """Abstract base class for reading/writing raw bytes to a key/value store."""

    @abstractmethod
    def read(self, key: str) -> bytes | None:
        """Return the raw bytes stored at *key*, or None if the key does not exist."""

    @abstractmethod
    def write(self, key: str, data: bytes) -> None:
        """Write *data* to *key*, overwriting any previous value."""


class S3Storage(Storage):
    """Production backend – reads and writes objects in an S3 bucket."""

    def __init__(self, bucket: str):
        import boto3  # imported lazily so the module works without boto3 in tests

        self._bucket = bucket
        self._s3 = boto3.client("s3")

    def read(self, key: str) -> bytes | None:
        try:
            obj = self._s3.get_object(Bucket=self._bucket, Key=key)
            return obj["Body"].read()
        except self._s3.exceptions.NoSuchKey:
            return None

    def write(self, key: str, data: bytes) -> None:
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=data)


class LocalStorage(Storage):
    """Local-filesystem backend - useful for unit tests and local development."""

    def __init__(self, base_dir: str = "."):
        self._base_dir = base_dir

    def _path(self, key: str) -> str:
        return os.path.join(self._base_dir, key)

    def read(self, key: str) -> bytes | None:
        path = self._path(key)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def write(self, key: str, data: bytes) -> None:
        path = self._path(key)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)


# ---------------------------------------------------------------------------
# Date cache
# ---------------------------------------------------------------------------


class DateCache:
    """Persists a list of dates as JSON via a Storage backend and detects new ones."""

    def __init__(self, storage: Storage, key: str):
        self._storage = storage
        self._key = key
        self._dates: list[dt.date] = self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dates_to_strings(dates: list[dt.date]) -> list[str]:
        return [d.isoformat() for d in dates]

    @staticmethod
    def _strings_to_dates(strings: list[str]) -> list[dt.date]:
        return [dt.date.fromisoformat(s) for s in strings]

    def _load(self) -> list[dt.date]:
        raw = self._storage.read(self._key)
        if raw is None:
            return []
        return self._strings_to_dates(json.loads(raw))

    def save(self) -> None:
        """Persist the current date list back to storage."""
        self._storage.write(
            self._key, json.dumps(self._dates_to_strings(self._dates)).encode()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def dates(self) -> list[dt.date]:
        return list(self._dates)

    def find_new_dates(self, current_dates: list[dt.date]) -> list[dt.date]:
        """Return dates in *current_dates* that are not already cached."""
        return list(set(current_dates) - set(self._dates))

    def update(self, dates: list[dt.date]) -> None:
        """Replace the cached dates and persist them to storage."""
        self._dates = list(dates)
        self.save()
