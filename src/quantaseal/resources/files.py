"""Files resource for encrypted file storage and retrieval."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


def _b64_encode(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode("ascii")


class Files:
    """Synchronous encrypted file storage operations.

    Unlike the MFT resource (which handles external transfers), this resource
    manages files stored directly in QuantaSeal's secure file store.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Upload and encrypt a file
        meta = qs.files.upload(
            b"<pdf content>",
            filename="contract.pdf",
            encrypt=True,
        )
        file_id = meta["id"]

        # Download
        content = qs.files.download(file_id)

        # List all files
        files = qs.files.list()

        # Delete
        qs.files.delete(file_id)
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def upload(
        self,
        file_path_or_bytes: Union[str, bytes],
        filename: str,
        encrypt: bool = True,
    ) -> dict[str, Any]:
        """Upload a file to secure storage.

        Args:
            file_path_or_bytes: File system path string or raw bytes.
            filename: Target filename for storage.
            encrypt: Encrypt the file at rest (default ``True``).

        Returns:
            Dict with ``id``, ``filename``, ``size_bytes``, ``encrypted``,
            ``content_type``, and ``created_at``.
        """
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            with open(file_path_or_bytes, "rb") as fh:
                content_b64 = _b64_encode(fh.read())
        else:
            content_b64 = _b64_encode(file_path_or_bytes)

        resp = self._transport.request(
            "POST",
            "/api/v2/files",
            json={"filename": filename, "content": content_b64, "encrypt": encrypt},
        )
        return resp.data or {}

    def download(self, file_id: str) -> bytes:
        """Download a file from secure storage.

        Args:
            file_id: UUID of the file.

        Returns:
            Raw file bytes.

        Raises:
            NotFoundError: If the file does not exist.
        """
        import base64

        resp = self._transport.request("GET", f"/api/v2/files/{file_id}/download")
        data = resp.data or {}
        return base64.b64decode(data.get("content", ""))

    def list(self) -> list[dict[str, Any]]:
        """List all files in secure storage.

        Returns:
            List of file metadata dicts (no content).
        """
        resp = self._transport.request("GET", "/api/v2/files")
        return resp.data or []

    def delete(self, file_id: str) -> None:
        """Delete a file from secure storage.

        Args:
            file_id: UUID of the file to delete.

        Raises:
            NotFoundError: If the file does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/files/{file_id}")

    def get_metadata(self, file_id: str) -> dict[str, Any]:
        """Get metadata for a file without downloading its content.

        Args:
            file_id: UUID of the file.

        Returns:
            Dict with ``id``, ``filename``, ``size_bytes``, ``encrypted``,
            ``content_type``, ``created_at``, and ``last_accessed_at``.

        Raises:
            NotFoundError: If the file does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/files/{file_id}")
        return resp.data or {}


class AsyncFiles:
    """Asynchronous file storage operations.

    Same API surface as ``Files`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def upload(
        self,
        file_path_or_bytes: Union[str, bytes],
        filename: str,
        encrypt: bool = True,
    ) -> dict[str, Any]:
        """Upload a file. See ``Files.upload`` for details."""
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            with open(file_path_or_bytes, "rb") as fh:
                content_b64 = _b64_encode(fh.read())
        else:
            content_b64 = _b64_encode(file_path_or_bytes)

        resp = await self._transport.request(
            "POST",
            "/api/v2/files",
            json={"filename": filename, "content": content_b64, "encrypt": encrypt},
        )
        return resp.data or {}

    async def download(self, file_id: str) -> bytes:
        """Download a file. See ``Files.download`` for details."""
        import base64

        resp = await self._transport.request("GET", f"/api/v2/files/{file_id}/download")
        data = resp.data or {}
        return base64.b64decode(data.get("content", ""))

    async def list(self) -> list[dict[str, Any]]:
        """List files. See ``Files.list`` for details."""
        resp = await self._transport.request("GET", "/api/v2/files")
        return resp.data or []

    async def delete(self, file_id: str) -> None:
        """Delete a file. See ``Files.delete`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/files/{file_id}")

    async def get_metadata(self, file_id: str) -> dict[str, Any]:
        """Get file metadata. See ``Files.get_metadata`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/files/{file_id}")
        return resp.data or {}
