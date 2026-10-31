"""
Storage Backend Abstraction for CareerLens.
Provides a modular interface for file storage operations, decoupling the application
from direct filesystem access and enabling future cloud storage providers (S3/GCS).
"""

import os
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings


class StorageBackend(ABC):
    """
    Abstract Base Class defining the storage interface.
    """

    @abstractmethod
    def save(self, category: str, filename: str, content: bytes) -> str:
        """
        Persist content under the given category and filename.
        Returns the resolved path or storage URI.
        """
        pass

    @abstractmethod
    def get_path(self, category: str, filename: str) -> str:
        """
        Return the local filesystem path for a stored file
        (used for local processing such as PDF text extraction and OCR).
        """
        pass

    @abstractmethod
    def read(self, category: str, filename: str) -> bytes:
        """
        Read and return the raw byte contents of the file.
        """
        pass

    @abstractmethod
    def exists(self, category: str, filename: str) -> bool:
        """
        Return True if the file exists in storage, False otherwise.
        """
        pass

    @abstractmethod
    def delete(self, category: str, filename: str) -> bool:
        """
        Remove the file from storage. Returns True if deleted, False if not found.
        """
        pass


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem implementation of StorageBackend.
    Safely scopes all file operations to settings.UPLOAD_DIR and prevents path traversal.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or settings.UPLOAD_DIR)
        os.makedirs(os.path.join(self.base_dir, "resumes"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "certificates"), exist_ok=True)

    def _resolve(self, category: str, filename: str) -> str:
        clean_name = os.path.basename(filename)
        if not clean_name or clean_name != filename or ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError(f"Invalid filename or path traversal detected: {filename}")

        cat_dir = os.path.abspath(os.path.join(self.base_dir, category))
        resolved = os.path.abspath(os.path.join(cat_dir, clean_name))

        if not resolved.startswith(cat_dir):
            raise ValueError(f"Path traversal detected: {filename}")

        return resolved

    def save(self, category: str, filename: str, content: bytes) -> str:
        path = self._resolve(category, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        return path

    def get_path(self, category: str, filename: str) -> str:
        return self._resolve(category, filename)

    def read(self, category: str, filename: str) -> bytes:
        path = self._resolve(category, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Stored file not found: {category}/{filename}")
        with open(path, "rb") as f:
            return f.read()

    def exists(self, category: str, filename: str) -> bool:
        try:
            path = self._resolve(category, filename)
            return os.path.exists(path)
        except Exception:
            return False

    def delete(self, category: str, filename: str) -> bool:
        try:
            path = self._resolve(category, filename)
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        except Exception:
            return False


# Singleton storage instance for application use
storage_backend: StorageBackend = LocalStorageBackend()
