"""Metrics resource for usage and performance statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Metrics:
    """Synchronous metrics and usage statistics.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Overall usage for the last 30 days
        usage = qs.metrics.get_usage("30d")

        # Encryption-specific stats
        enc_stats = qs.metrics.get_encryption_stats()
        print(enc_stats["total_operations"], enc_stats["avg_latency_ms"])

        # Vault stats
        vault_stats = qs.metrics.get_vault_stats()
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get_usage(self, period: str = "30d") -> dict[str, Any]:
        """Get aggregate usage metrics for a time period.

        Args:
            period: Time period string. Common values: ``7d``, ``30d``, ``90d``,
                ``1y``, or an ISO 8601 interval like ``2026-01-01/2026-03-31``.

        Returns:
            Dict with operation counts, cost estimates, and trend data.
        """
        resp = self._transport.request(
            "GET", "/api/v2/metrics/usage", params={"period": period}
        )
        return resp.data or {}

    def get_encryption_stats(self) -> dict[str, Any]:
        """Get encryption operation statistics.

        Returns:
            Dict with ``total_operations``, ``avg_latency_ms``,
            ``p99_latency_ms``, ``algorithms_used``, and ``key_ids_active``.
        """
        resp = self._transport.request("GET", "/api/v2/metrics/encryption")
        return resp.data or {}

    def get_api_stats(self, period: str = "30d") -> dict[str, Any]:
        """Get API call statistics for a time period.

        Args:
            period: Time period string (same format as ``get_usage``).

        Returns:
            Dict with ``total_calls``, ``error_rate``, ``p50_latency_ms``,
            ``p99_latency_ms``, ``calls_by_endpoint``, and ``calls_by_day``.
        """
        resp = self._transport.request(
            "GET", "/api/v2/metrics/api", params={"period": period}
        )
        return resp.data or {}

    def get_vault_stats(self) -> dict[str, Any]:
        """Get vault usage statistics.

        Returns:
            Dict with ``total_entries``, ``active_entries``, ``expiring_soon``,
            ``seal_operations``, ``unseal_operations``, and ``rotate_operations``.
        """
        resp = self._transport.request("GET", "/api/v2/metrics/vault")
        return resp.data or {}


class AsyncMetrics:
    """Asynchronous metrics operations.

    Same API surface as ``Metrics`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get_usage(self, period: str = "30d") -> dict[str, Any]:
        """Get usage metrics. See ``Metrics.get_usage`` for details."""
        resp = await self._transport.request(
            "GET", "/api/v2/metrics/usage", params={"period": period}
        )
        return resp.data or {}

    async def get_encryption_stats(self) -> dict[str, Any]:
        """Get encryption stats. See ``Metrics.get_encryption_stats`` for details."""
        resp = await self._transport.request("GET", "/api/v2/metrics/encryption")
        return resp.data or {}

    async def get_api_stats(self, period: str = "30d") -> dict[str, Any]:
        """Get API stats. See ``Metrics.get_api_stats`` for details."""
        resp = await self._transport.request(
            "GET", "/api/v2/metrics/api", params={"period": period}
        )
        return resp.data or {}

    async def get_vault_stats(self) -> dict[str, Any]:
        """Get vault stats. See ``Metrics.get_vault_stats`` for details."""
        resp = await self._transport.request("GET", "/api/v2/metrics/vault")
        return resp.data or {}
