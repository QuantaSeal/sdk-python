"""Tokenize resource for data tokenization and detokenization."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Tokenize:
    """Synchronous tokenization operations - tokenize, detokenize, and batch variants.

    Tokens are opaque, non-reversible references that replace sensitive data
    (PAN, SSN, etc.) while preserving format for downstream systems.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Tokenize a credit card number (format-preserving)
        result = qs.tokenize.tokenize(
            data="4111111111111111",
            data_type="pan",
            format_preserving=True,
        )
        token = result["token"]  # e.g. "4XXX-XXXX-XXXX-1111"

        # Detokenize back
        original = qs.tokenize.detokenize(token)
        print(original["data"])  # "4111111111111111"

        # Batch tokenize
        results = qs.tokenize.batch_tokenize([
            {"data": "123-45-6789", "data_type": "ssn"},
            {"data": "user@example.com", "data_type": "email"},
        ])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def tokenize(
        self,
        data: str,
        data_type: str,
        format_preserving: bool = False,
    ) -> dict[str, Any]:
        """Tokenize a single data value.

        Args:
            data: The sensitive data string to tokenize.
            data_type: Semantic type of the data (e.g. ``pan``, ``ssn``, ``email``,
                ``phone``, ``generic``).
            format_preserving: If ``True``, the token preserves the length and
                format of the original value (requires supported ``data_type``).

        Returns:
            Dict with ``token`` and ``data_type``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/tokenize",
            json={
                "data": data,
                "data_type": data_type,
                "format_preserving": format_preserving,
            },
        )
        return resp.data or {}

    def detokenize(self, token: str) -> dict[str, Any]:
        """Retrieve the original value for a token.

        Args:
            token: Opaque token string returned by ``tokenize()``.

        Returns:
            Dict with ``data`` (original value) and ``data_type``.

        Raises:
            NotFoundError: If the token does not exist or has been revoked.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/detokenize",
            json={"token": token},
        )
        return resp.data or {}

    def batch_tokenize(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Tokenize multiple values in a single request.

        Args:
            items: List of dicts, each with ``data``, ``data_type``, and optional
                ``format_preserving`` key.

        Returns:
            List of result dicts in the same order as ``items``, each with ``token``
            and ``data_type``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/tokenize/batch",
            json={"items": items},
        )
        return resp.data or []

    def batch_detokenize(self, tokens: list[str]) -> list[dict[str, Any]]:
        """Detokenize multiple tokens in a single request.

        Args:
            tokens: List of token strings to resolve.

        Returns:
            List of result dicts in the same order as ``tokens``, each with
            ``token``, ``data``, and ``data_type``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/detokenize/batch",
            json={"tokens": tokens},
        )
        return resp.data or []


class AsyncTokenize:
    """Asynchronous tokenization operations.

    Same API surface as ``Tokenize`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def tokenize(
        self,
        data: str,
        data_type: str,
        format_preserving: bool = False,
    ) -> dict[str, Any]:
        """Tokenize a value. See ``Tokenize.tokenize`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/tokenize",
            json={
                "data": data,
                "data_type": data_type,
                "format_preserving": format_preserving,
            },
        )
        return resp.data or {}

    async def detokenize(self, token: str) -> dict[str, Any]:
        """Detokenize a token. See ``Tokenize.detokenize`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/detokenize",
            json={"token": token},
        )
        return resp.data or {}

    async def batch_tokenize(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Batch tokenize. See ``Tokenize.batch_tokenize`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/tokenize/batch",
            json={"items": items},
        )
        return resp.data or []

    async def batch_detokenize(self, tokens: list[str]) -> list[dict[str, Any]]:
        """Batch detokenize. See ``Tokenize.batch_detokenize`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/detokenize/batch",
            json={"tokens": tokens},
        )
        return resp.data or []
