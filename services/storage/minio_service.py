import os
import logging
import asyncio
from typing import Optional
from minio import Minio
from minio.error import S3Error
from apps.api.app.core.config import settings

logger = logging.getLogger(__name__)


class MinIOService:
    """Service to interact with MinIO S3 Object Storage asynchronously without blocking the event loop."""

    def __init__(self):
        endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
        self.client = Minio(
            endpoint=endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_sync()

    def _ensure_bucket_sync(self):
        """Initial bucket check at startup."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: '{self.bucket_name}'")
        except Exception as e:
            logger.warning(f"Could not connect or check MinIO bucket '{self.bucket_name}': {e}")

    async def ensure_bucket_async(self):
        """Async bucket check using thread pool to avoid event loop blocking."""
        try:
            exists = await asyncio.to_thread(self.client.bucket_exists, self.bucket_name)
            if not exists:
                await asyncio.to_thread(self.client.make_bucket, self.bucket_name)
                logger.info(f"Created MinIO bucket: '{self.bucket_name}'")
        except Exception as e:
            logger.warning(f"Could not connect or check MinIO bucket '{self.bucket_name}': {e}")

    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> bool:
        """Synchronous file upload to MinIO."""
        if not os.path.exists(file_path):
            logger.error(f"File not found for MinIO upload: {file_path}")
            return False

        obj_name = object_name or os.path.basename(file_path)
        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=obj_name,
                file_path=file_path
            )
            logger.info(f"File '{file_path}' successfully uploaded to MinIO as '{obj_name}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload '{file_path}' to MinIO: {e}")
            return False

    async def upload_file_async(self, file_path: str, object_name: Optional[str] = None) -> bool:
        """Asynchronous non-blocking file upload to MinIO via thread pool."""
        return await asyncio.to_thread(self.upload_file, file_path, object_name)

    def download_file(self, object_name: str, target_path: str) -> bool:
        """Synchronous file download from MinIO."""
        try:
            self.client.fget_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=target_path
            )
            logger.info(f"Downloaded '{object_name}' from MinIO to '{target_path}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to download '{object_name}' from MinIO: {e}")
            return False

    async def download_file_async(self, object_name: str, target_path: str) -> bool:
        """Asynchronous non-blocking file download from MinIO via thread pool."""
        return await asyncio.to_thread(self.download_file, object_name, target_path)


minio_service = MinIOService()
