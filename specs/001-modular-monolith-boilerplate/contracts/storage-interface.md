# Storage Interface Protocol Contract (`core/storage`)

## Protocol Definition (`core/storage/interface.py`)

```python
from typing import BinaryIO, Protocol

class StorageInterface(Protocol):
    """Abstract storage interface for object/file management."""

    async def upload(
        self,
        file_obj: BinaryIO,
        destination_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Uploads a file stream to object storage and returns the storage URI or path."""
        ...

    async def get_download_url(
        self,
        storage_path: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        """Generates a pre-signed or direct download URL for the target object."""
        ...

    async def delete(self, storage_path: str) -> bool:
        """Removes the target object from storage."""
        ...

    async def exists(self, storage_path: str) -> bool:
        """Checks if the object exists in storage."""
        ...
```

## Production Implementation: `MinioStorageAdapter` (`core/storage/minio_adapter.py`)
Implements `StorageInterface` using `boto3` or `aioboto3` connecting to MinIO (local dev) or AWS S3 (production).
Bound via `core/storage/di.py` (`StorageProvider`).
