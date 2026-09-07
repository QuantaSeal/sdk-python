"""MFT (Managed File Transfer) resource for secure file transfer operations."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class MFT:
    """Synchronous Managed File Transfer operations.

    Files are encrypted in transit and at rest using the tenant's quantum-safe
    key material.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Upload a file
        transfer = qs.mft.upload(
            "/path/to/report.pdf",
            filename="q1-report.pdf",
            destination="s3://my-bucket/reports/",
            encrypt=True,
        )
        transfer_id = transfer["id"]

        # Download
        file_bytes = qs.mft.download(transfer_id)

        # List transfers
        transfers = qs.mft.list_transfers()
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def upload(
        self,
        file_path_or_bytes: Union[str, bytes],
        filename: str,
        destination: str | None = None,
        encrypt: bool = True,
    ) -> dict[str, Any]:
        """Upload a file via Managed File Transfer.

        Args:
            file_path_or_bytes: Either a file system path string or raw bytes.
            filename: Destination filename.
            destination: Optional destination URI (e.g. ``s3://bucket/prefix/``).
                Defaults to the tenant's configured default destination.
            encrypt: Whether to encrypt the file at rest (default ``True``).

        Returns:
            Dict with ``id``, ``filename``, ``size_bytes``, ``destination``,
            ``encrypted``, and ``created_at``.
        """
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            with open(file_path_or_bytes, "rb") as fh:
                content_b64 = _b64(fh.read())
        else:
            content_b64 = _b64(file_path_or_bytes)

        body: dict[str, Any] = {
            "filename": filename,
            "content": content_b64,
            "encrypt": encrypt,
        }
        if destination is not None:
            body["destination"] = destination

        resp = self._transport.request("POST", "/api/v2/mft/upload", json=body)
        return resp.data or {}

    def download(self, transfer_id: str) -> bytes:
        """Download a transferred file.

        Args:
            transfer_id: UUID of the transfer returned by ``upload()``.

        Returns:
            Raw file bytes.

        Raises:
            NotFoundError: If the transfer does not exist.
        """
        import base64

        resp = self._transport.request("GET", f"/api/v2/mft/download/{transfer_id}")
        data = resp.data or {}
        return base64.b64decode(data.get("content", ""))

    def list_transfers(self) -> list[dict[str, Any]]:
        """List all file transfers for the tenant.

        Returns:
            List of transfer metadata dicts.
        """
        resp = self._transport.request("GET", "/api/v2/mft/transfers")
        return resp.data or []

    def get_transfer(self, transfer_id: str) -> dict[str, Any]:
        """Get metadata for a specific file transfer.

        Args:
            transfer_id: UUID of the transfer.

        Returns:
            Transfer metadata dict.

        Raises:
            NotFoundError: If the transfer does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/mft/transfers/{transfer_id}")
        return resp.data or {}

    def delete_transfer(self, transfer_id: str) -> None:
        """Delete a file transfer and its stored file.

        Args:
            transfer_id: UUID of the transfer to delete.

        Raises:
            NotFoundError: If the transfer does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/mft/transfers/{transfer_id}")


def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode("ascii")


class AsyncMFT:
    """Asynchronous Managed File Transfer operations.

    Same API surface as ``MFT`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def upload(
        self,
        file_path_or_bytes: Union[str, bytes],
        filename: str,
        destination: str | None = None,
        encrypt: bool = True,
    ) -> dict[str, Any]:
        """Upload a file. See ``MFT.upload`` for details."""
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            with open(file_path_or_bytes, "rb") as fh:
                content_b64 = _b64(fh.read())
        else:
            content_b64 = _b64(file_path_or_bytes)

        body: dict[str, Any] = {
            "filename": filename,
            "content": content_b64,
            "encrypt": encrypt,
        }
        if destination is not None:
            body["destination"] = destination

        resp = await self._transport.request("POST", "/api/v2/mft/upload", json=body)
        return resp.data or {}

    async def download(self, transfer_id: str) -> bytes:
        """Download a file. See ``MFT.download`` for details."""
        import base64

        resp = await self._transport.request("GET", f"/api/v2/mft/download/{transfer_id}")
        data = resp.data or {}
        return base64.b64decode(data.get("content", ""))

    async def list_transfers(self) -> list[dict[str, Any]]:
        """List transfers. See ``MFT.list_transfers`` for details."""
        resp = await self._transport.request("GET", "/api/v2/mft/transfers")
        return resp.data or []

    async def get_transfer(self, transfer_id: str) -> dict[str, Any]:
        """Get transfer metadata. See ``MFT.get_transfer`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/mft/transfers/{transfer_id}")
        return resp.data or {}

    async def delete_transfer(self, transfer_id: str) -> None:
        """Delete a transfer. See ``MFT.delete_transfer`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/mft/transfers/{transfer_id}")
