"""Sync resource for data synchronisation job management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Sync:
    """Synchronous data sync job management.

    Sync jobs move data between an external integration and QuantaSeal
    (or vice-versa) on a scheduled or on-demand basis.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Create a nightly inbound sync job
        job = qs.sync.create_job(
            integration_id="int_abc123",
            direction="inbound",
            schedule="0 2 * * *",  # cron: 02:00 UTC daily
        )

        # Trigger a job immediately
        qs.sync.trigger_job(job["id"])

        # Check execution history
        history = qs.sync.get_job_history(job["id"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create_job(
        self,
        integration_id: str,
        direction: str,
        schedule: str | None = None,
    ) -> dict[str, Any]:
        """Create a new sync job.

        Args:
            integration_id: UUID of the integration to sync.
            direction: ``inbound`` (pull from external) or ``outbound`` (push to external).
            schedule: Optional cron expression for automatic scheduling.
                Omit for manual / on-demand-only jobs.

        Returns:
            Dict with ``id``, ``integration_id``, ``direction``, ``schedule``,
            ``status``, and ``created_at``.
        """
        body: dict[str, Any] = {
            "integration_id": integration_id,
            "direction": direction,
        }
        if schedule is not None:
            body["schedule"] = schedule

        resp = self._transport.request("POST", "/api/v2/sync/jobs", json=body)
        return resp.data or {}

    def list_jobs(self) -> list[dict[str, Any]]:
        """List all sync jobs for the tenant.

        Returns:
            List of sync job metadata dicts.
        """
        resp = self._transport.request("GET", "/api/v2/sync/jobs")
        return resp.data or []

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Get a sync job by ID.

        Args:
            job_id: UUID of the sync job.

        Returns:
            Sync job metadata dict.

        Raises:
            NotFoundError: If the job does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/sync/jobs/{job_id}")
        return resp.data or {}

    def trigger_job(self, job_id: str) -> dict[str, Any]:
        """Trigger an immediate run of a sync job.

        Args:
            job_id: UUID of the sync job to trigger.

        Returns:
            Dict with ``execution_id``, ``status``, and ``triggered_at``.
        """
        resp = self._transport.request("POST", f"/api/v2/sync/jobs/{job_id}/trigger")
        return resp.data or {}

    def delete_job(self, job_id: str) -> None:
        """Delete a sync job.

        Args:
            job_id: UUID of the sync job to delete.

        Raises:
            NotFoundError: If the job does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/sync/jobs/{job_id}")

    def get_job_history(self, job_id: str) -> list[dict[str, Any]]:
        """Get execution history for a sync job.

        Args:
            job_id: UUID of the sync job.

        Returns:
            List of execution records with ``execution_id``, ``status``,
            ``started_at``, ``finished_at``, and ``records_synced``.
        """
        resp = self._transport.request("GET", f"/api/v2/sync/jobs/{job_id}/history")
        return resp.data or []


class AsyncSync:
    """Asynchronous sync job management.

    Same API surface as ``Sync`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create_job(
        self,
        integration_id: str,
        direction: str,
        schedule: str | None = None,
    ) -> dict[str, Any]:
        """Create a sync job. See ``Sync.create_job`` for details."""
        body: dict[str, Any] = {
            "integration_id": integration_id,
            "direction": direction,
        }
        if schedule is not None:
            body["schedule"] = schedule

        resp = await self._transport.request("POST", "/api/v2/sync/jobs", json=body)
        return resp.data or {}

    async def list_jobs(self) -> list[dict[str, Any]]:
        """List sync jobs. See ``Sync.list_jobs`` for details."""
        resp = await self._transport.request("GET", "/api/v2/sync/jobs")
        return resp.data or []

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """Get a sync job. See ``Sync.get_job`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/sync/jobs/{job_id}")
        return resp.data or {}

    async def trigger_job(self, job_id: str) -> dict[str, Any]:
        """Trigger a sync job. See ``Sync.trigger_job`` for details."""
        resp = await self._transport.request(
            "POST", f"/api/v2/sync/jobs/{job_id}/trigger"
        )
        return resp.data or {}

    async def delete_job(self, job_id: str) -> None:
        """Delete a sync job. See ``Sync.delete_job`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/sync/jobs/{job_id}")

    async def get_job_history(self, job_id: str) -> list[dict[str, Any]]:
        """Get job execution history. See ``Sync.get_job_history`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/sync/jobs/{job_id}/history"
        )
        return resp.data or []
