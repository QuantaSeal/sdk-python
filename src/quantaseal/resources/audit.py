"""Audit resource for audit log access and export."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Audit:
    """Synchronous audit log operations.

    All API operations in QuantaSeal produce immutable, tamper-evident audit
    log entries. This resource lets you query, inspect, and export them.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # List recent encryption events
        logs = qs.audit.list(limit=50, event_type="encryption.encrypt")

        # Get a specific log entry
        entry = qs.audit.get(log_id="log_abc123")

        # Export a date range as CSV
        csv_bytes = qs.audit.export(
            format="csv",
            start_date="2026-01-01T00:00:00Z",
            end_date="2026-03-31T23:59:59Z",
        )
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """List audit log entries.

        Args:
            limit: Maximum number of entries to return (default 100, max 1000).
            offset: Pagination offset (default 0).
            event_type: Filter by event type (e.g. ``encryption.encrypt``,
                ``vault.seal``, ``auth.login``).
            start_date: ISO 8601 start timestamp for date range filtering.
            end_date: ISO 8601 end timestamp for date range filtering.

        Returns:
            List of audit log entry dicts.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if event_type is not None:
            params["event_type"] = event_type
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date

        resp = self._transport.request("GET", "/api/v2/audit/logs", params=params)
        return resp.data or []

    def get(self, log_id: str) -> dict[str, Any]:
        """Get a single audit log entry.

        Args:
            log_id: UUID of the log entry.

        Returns:
            Full audit log entry dict with event details and request metadata.

        Raises:
            NotFoundError: If the log entry does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/audit/logs/{log_id}")
        return resp.data or {}

    def export(
        self,
        format: str = "json",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Export audit logs for a date range.

        Args:
            format: Export format - ``json`` or ``csv`` (default ``json``).
            start_date: ISO 8601 start timestamp (inclusive).
            end_date: ISO 8601 end timestamp (inclusive).

        Returns:
            Dict with ``download_url`` (pre-signed URL) and ``expires_at``,
            or inline ``content`` for small exports.
        """
        body: dict[str, Any] = {"format": format}
        if start_date is not None:
            body["start_date"] = start_date
        if end_date is not None:
            body["end_date"] = end_date

        resp = self._transport.request("POST", "/api/v2/audit/export", json=body)
        return resp.data or {}


class AsyncAudit:
    """Asynchronous audit log operations.

    Same API surface as ``Audit`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """List audit logs. See ``Audit.list`` for details."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if event_type is not None:
            params["event_type"] = event_type
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date

        resp = await self._transport.request("GET", "/api/v2/audit/logs", params=params)
        return resp.data or []

    async def get(self, log_id: str) -> dict[str, Any]:
        """Get an audit log entry. See ``Audit.get`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/audit/logs/{log_id}")
        return resp.data or {}

    async def export(
        self,
        format: str = "json",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Export audit logs. See ``Audit.export`` for details."""
        body: dict[str, Any] = {"format": format}
        if start_date is not None:
            body["start_date"] = start_date
        if end_date is not None:
            body["end_date"] = end_date

        resp = await self._transport.request("POST", "/api/v2/audit/export", json=body)
        return resp.data or {}
