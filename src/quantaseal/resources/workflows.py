"""Workflows resource for automation workflow management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Workflows:
    """Synchronous workflow automation operations.

    Workflows chain triggers and steps to automate security and compliance
    processes (e.g. re-encrypt on key rotation, alert on failed verification).

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Create a workflow
        wf = qs.workflows.create(
            name="Key Rotation Alert",
            trigger={"type": "event", "event": "vault.key_rotated"},
            steps=[
                {"type": "notify", "channel": "slack", "message": "Key rotated: {{entry_id}}"},
            ],
        )

        # Manually trigger it
        execution = qs.workflows.trigger(wf["id"], payload={"entry_id": "abc"})

        # View past executions
        executions = qs.workflows.get_executions(wf["id"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create(
        self,
        name: str,
        trigger: dict[str, Any],
        steps: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a new workflow.

        Args:
            name: Human-readable workflow name.
            trigger: Trigger definition dict (``type``, ``event``, ``schedule``, etc.).
            steps: Ordered list of step definition dicts.

        Returns:
            Dict with ``id``, ``name``, ``status``, and ``created_at``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/workflows",
            json={"name": name, "trigger": trigger, "steps": steps},
        )
        return resp.data or {}

    def list(self) -> list[dict[str, Any]]:
        """List all workflows.

        Returns:
            List of workflow metadata dicts.
        """
        resp = self._transport.request("GET", "/api/v2/workflows")
        return resp.data or []

    def get(self, workflow_id: str) -> dict[str, Any]:
        """Get a workflow by ID.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            Full workflow definition dict including steps.

        Raises:
            NotFoundError: If the workflow does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/workflows/{workflow_id}")
        return resp.data or {}

    def trigger(
        self,
        workflow_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Manually trigger a workflow execution.

        Args:
            workflow_id: UUID of the workflow to run.
            payload: Optional context payload passed to the workflow steps.

        Returns:
            Dict with ``execution_id``, ``status``, and ``triggered_at``.
        """
        body: dict[str, Any] = {}
        if payload is not None:
            body["payload"] = payload

        resp = self._transport.request(
            "POST", f"/api/v2/workflows/{workflow_id}/trigger", json=body
        )
        return resp.data or {}

    def update(self, workflow_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a workflow's name, trigger, or steps.

        Args:
            workflow_id: UUID of the workflow to update.
            updates: Dict of fields to update (any subset of ``name``,
                ``trigger``, ``steps``, ``status``).

        Returns:
            Updated workflow dict.

        Raises:
            NotFoundError: If the workflow does not exist.
        """
        resp = self._transport.request(
            "PATCH", f"/api/v2/workflows/{workflow_id}", json=updates
        )
        return resp.data or {}

    def delete(self, workflow_id: str) -> None:
        """Delete a workflow.

        Args:
            workflow_id: UUID of the workflow to delete.

        Raises:
            NotFoundError: If the workflow does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/workflows/{workflow_id}")

    def get_executions(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get execution history for a workflow.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            List of execution records with ``execution_id``, ``status``,
            ``triggered_at``, ``finished_at``, and ``error`` (if failed).
        """
        resp = self._transport.request(
            "GET", f"/api/v2/workflows/{workflow_id}/executions"
        )
        return resp.data or []


class AsyncWorkflows:
    """Asynchronous workflow operations.

    Same API surface as ``Workflows`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        name: str,
        trigger: dict[str, Any],
        steps: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a workflow. See ``Workflows.create`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/workflows",
            json={"name": name, "trigger": trigger, "steps": steps},
        )
        return resp.data or {}

    async def list(self) -> list[dict[str, Any]]:
        """List workflows. See ``Workflows.list`` for details."""
        resp = await self._transport.request("GET", "/api/v2/workflows")
        return resp.data or []

    async def get(self, workflow_id: str) -> dict[str, Any]:
        """Get a workflow. See ``Workflows.get`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/workflows/{workflow_id}")
        return resp.data or {}

    async def trigger(
        self,
        workflow_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Trigger a workflow. See ``Workflows.trigger`` for details."""
        body: dict[str, Any] = {}
        if payload is not None:
            body["payload"] = payload

        resp = await self._transport.request(
            "POST", f"/api/v2/workflows/{workflow_id}/trigger", json=body
        )
        return resp.data or {}

    async def update(self, workflow_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a workflow. See ``Workflows.update`` for details."""
        resp = await self._transport.request(
            "PATCH", f"/api/v2/workflows/{workflow_id}", json=updates
        )
        return resp.data or {}

    async def delete(self, workflow_id: str) -> None:
        """Delete a workflow. See ``Workflows.delete`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/workflows/{workflow_id}")

    async def get_executions(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get workflow executions. See ``Workflows.get_executions`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/workflows/{workflow_id}/executions"
        )
        return resp.data or []
