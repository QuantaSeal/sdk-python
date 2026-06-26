"""Proxy resource for integration management and request forwarding."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Proxy:
    """Synchronous proxy and integration management operations.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Register an integration
        integration = qs.proxy.create_integration(
            name="Salesforce Prod",
            system_type="salesforce",
            config={"instance_url": "https://na1.salesforce.com"},
            endpoint_url="https://na1.salesforce.com/services/data/v57.0",
            allowed_operations=["read", "write"],
        )

        # Forward a request through the integration
        result = qs.proxy.forward(
            integration_id=integration["id"],
            method="GET",
            endpoint="/sobjects/Account",
        )
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create_integration(
        self,
        name: str,
        system_type: str,
        config: dict[str, Any],
        endpoint_url: str,
        allowed_operations: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register a new external integration.

        Args:
            name: Human-readable integration name.
            system_type: System type identifier (e.g. ``salesforce``, ``postgres``).
            config: System-specific configuration dictionary (credentials, options).
            endpoint_url: Base URL of the target system.
            allowed_operations: Permitted operations (default: all).

        Returns:
            Dict representing the created integration with ``id``, ``name``, and status.
        """
        body: dict[str, Any] = {
            "name": name,
            "system_type": system_type,
            "config": config,
            "endpoint_url": endpoint_url,
        }
        if allowed_operations is not None:
            body["allowed_operations"] = allowed_operations

        resp = self._transport.request("POST", "/api/v2/integrations", json=body)
        return resp.data or {}

    def list_integrations(self) -> list[dict[str, Any]]:
        """List all registered integrations.

        Returns:
            List of integration metadata dicts.
        """
        resp = self._transport.request("GET", "/api/v2/integrations")
        return resp.data or []

    def get_integration(self, integration_id: str) -> dict[str, Any]:
        """Get a single integration by ID.

        Args:
            integration_id: UUID of the integration.

        Returns:
            Integration metadata dict.

        Raises:
            NotFoundError: If no integration with that ID exists.
        """
        resp = self._transport.request("GET", f"/api/v2/integrations/{integration_id}")
        return resp.data or {}

    def delete_integration(self, integration_id: str) -> None:
        """Delete an integration.

        Args:
            integration_id: UUID of the integration to delete.

        Raises:
            NotFoundError: If no integration with that ID exists.
        """
        self._transport.request_raw("DELETE", f"/api/v2/integrations/{integration_id}")

    def test_connectivity(self, integration_id: str) -> dict[str, Any]:
        """Test connectivity to an integration's target system.

        Args:
            integration_id: UUID of the integration to test.

        Returns:
            Dict with ``success`` bool, ``latency_ms``, and optional ``error`` message.
        """
        resp = self._transport.request(
            "POST", f"/api/v2/integrations/{integration_id}/test"
        )
        return resp.data or {}

    def forward(
        self,
        integration_id: str,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Forward a request through an integration proxy.

        The request is routed via the QuantaSeal proxy, which injects
        encrypted credentials and audit-logs the operation.

        Args:
            integration_id: UUID of the integration to route through.
            method: HTTP method (``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``).
            endpoint: Target endpoint path relative to the integration's base URL.
            payload: Optional request body as a dictionary.
            headers: Optional additional HTTP headers to forward.

        Returns:
            Dict with ``status_code``, ``headers``, and ``body`` from the proxied response.
        """
        body: dict[str, Any] = {
            "integration_id": integration_id,
            "method": method,
            "endpoint": endpoint,
        }
        if payload is not None:
            body["payload"] = payload
        if headers is not None:
            body["headers"] = headers

        resp = self._transport.request("POST", "/api/v2/proxy/forward", json=body)
        return resp.data or {}


class AsyncProxy:
    """Asynchronous proxy and integration management operations.

    Same API surface as ``Proxy`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create_integration(
        self,
        name: str,
        system_type: str,
        config: dict[str, Any],
        endpoint_url: str,
        allowed_operations: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create an integration. See ``Proxy.create_integration`` for details."""
        body: dict[str, Any] = {
            "name": name,
            "system_type": system_type,
            "config": config,
            "endpoint_url": endpoint_url,
        }
        if allowed_operations is not None:
            body["allowed_operations"] = allowed_operations

        resp = await self._transport.request("POST", "/api/v2/integrations", json=body)
        return resp.data or {}

    async def list_integrations(self) -> list[dict[str, Any]]:
        """List integrations. See ``Proxy.list_integrations`` for details."""
        resp = await self._transport.request("GET", "/api/v2/integrations")
        return resp.data or []

    async def get_integration(self, integration_id: str) -> dict[str, Any]:
        """Get an integration. See ``Proxy.get_integration`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/integrations/{integration_id}")
        return resp.data or {}

    async def delete_integration(self, integration_id: str) -> None:
        """Delete an integration. See ``Proxy.delete_integration`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/integrations/{integration_id}")

    async def test_connectivity(self, integration_id: str) -> dict[str, Any]:
        """Test connectivity. See ``Proxy.test_connectivity`` for details."""
        resp = await self._transport.request(
            "POST", f"/api/v2/integrations/{integration_id}/test"
        )
        return resp.data or {}

    async def forward(
        self,
        integration_id: str,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Forward a proxied request. See ``Proxy.forward`` for details."""
        body: dict[str, Any] = {
            "integration_id": integration_id,
            "method": method,
            "endpoint": endpoint,
        }
        if payload is not None:
            body["payload"] = payload
        if headers is not None:
            body["headers"] = headers

        resp = await self._transport.request("POST", "/api/v2/proxy/forward", json=body)
        return resp.data or {}
