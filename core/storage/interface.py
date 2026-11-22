from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO


@dataclass(frozen=True)
class StoredObjectInfo:
    key: str
    size: int
    last_modified: datetime


class IStorageProvider(ABC):
    """Abstract interface for S3 / Object Storage Operations."""

    @abstractmethod
    async def upload(
        self,
        bucket: str,
        key: str,
        data: BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Upload data stream to object storage and return relative URI (e.g. /{bucket}/{key})."""

    @abstractmethod
    async def get_presigned_url(
        self, bucket: str, key: str, *, expires: int = 3600
    ) -> str:
        """Generate a presigned GET URL for temporary downloading."""

    @abstractmethod
    async def delete(self, bucket: str, key: str) -> None:
        """Remove object from storage."""

    @abstractmethod
    async def exists(self, bucket: str, key: str) -> bool:
        """Check if target object exists in storage."""
