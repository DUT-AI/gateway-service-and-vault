import asyncio
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from core.exceptions import StorageError
from core.storage.interface import IStorageProvider


class MinIOStorageAdapter(IStorageProvider):
    """S3 / MinIO storage adapter implementation."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
        public_endpoint_url: str | None = None,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.public_endpoint_url = (public_endpoint_url or endpoint_url).rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            verify=secure,
        )

    async def upload(
        self,
        bucket: str,
        key: str,
        data: BinaryIO,
        content_type: str | None = None,
    ) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        def _do_upload() -> None:
            self.client.upload_fileobj(data, bucket, key, ExtraArgs=extra_args)

        try:
            await asyncio.to_thread(_do_upload)
            return f"/{bucket}/{key}"
        except ClientError as e:
            raise StorageError(f"Failed to upload object {key}: {e}") from e

    async def get_presigned_url(
        self, bucket: str, key: str, *, expires: int = 3600
    ) -> str:
        try:
            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires,
            )
            return url
        except ClientError as e:
            raise StorageError(
                f"Failed to generate presigned url for {key}: {e}"
            ) from e

    async def delete(self, bucket: str, key: str) -> None:
        def _do_delete() -> None:
            self.client.delete_object(Bucket=bucket, Key=key)

        try:
            await asyncio.to_thread(_do_delete)
        except ClientError as e:
            raise StorageError(f"Failed to delete object {key}: {e}") from e

    async def exists(self, bucket: str, key: str) -> bool:
        def _do_head() -> bool:
            try:
                self.client.head_object(Bucket=bucket, Key=key)
                return True
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") in ("404", "NoSuchKey"):
                    return False
                raise

        try:
            return await asyncio.to_thread(_do_head)
        except Exception as e:
            raise StorageError(f"Failed to check existence for {key}: {e}") from e
