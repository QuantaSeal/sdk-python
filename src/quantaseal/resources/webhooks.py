"""Webhooks resource for webhook endpoint management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Webhooks:
    """Synchronous webhook management operations.

    QuantaSeal signs all webhook deliveries with an HMAC-SHA-256 signature in
    the ``X-QuantaSeal-Signature`` header so you can verify authenticity.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Register a webhook
        hook = qs.webhooks.create(
            url="https://myapp.example.com/hooks/qs",
            events=["vault.seal", "vault.unseal", "encryption.encrypt"],
            secret="whsec_...",
        )

        # Test delivery
        qs.webhooks.test(hook["id"])

        # View recent deliveries
        deliveries = qs.webhooks.list_deliveries(hook["id"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create(
        self,
        url: str,
        events: list[str],
        secret: str | None = None,
    ) -> dict[str, Any]:
        """Register a new webhook endpoint.

        Args:
            url: HTTPS URL to deliver events to.
            events: List of event types to subscribe to.  Use ``["*"]`` for all events.
            secret: Optional HMAC secret for signature verification.  If omitted,
                a secret is auto-generated and returned in the response.

        Returns:
            Dict with ``id``, ``url``, ``events``, ``secret`` (only on creation),
            and ``created_at``.
        """
        body: dict[str, Any] = {"url": url, "events": events}
        if secret is not None:
            body["secret"] = secret

        resp = self._transport.request("POST", "/api/v2/webhooks", json=body)
        return resp.data or {}

    def list(self) -> list[dict[str, Any]]:
        """List all registered webhooks.

        Returns:
            List of webhook metadata dicts (secrets are not returned).
        """
        resp = self._transport.request("GET", "/api/v2/webhooks")
        return resp.data or []

    def get(self, webhook_id: str) -> dict[str, Any]:
        """Get a webhook by ID.

        Args:
            webhook_id: UUID of the webhook.

        Returns:
            Webhook metadata dict.

        Raises:
            NotFoundError: If the webhook does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/webhooks/{webhook_id}")
        return resp.data or {}

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint.

        Args:
            webhook_id: UUID of the webhook to delete.

        Raises:
            NotFoundError: If the webhook does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> dict[str, Any]:
        """Send a test delivery to a webhook endpoint.

        Args:
            webhook_id: UUID of the webhook to test.

        Returns:
            Dict with ``delivery_id``, ``status_code``, and ``response_body``.
        """
        resp = self._transport.request("POST", f"/api/v2/webhooks/{webhook_id}/test")
        return resp.data or {}

    def list_deliveries(self, webhook_id: str) -> list[dict[str, Any]]:
        """List recent delivery attempts for a webhook.

        Args:
            webhook_id: UUID of the webhook.

        Returns:
            List of delivery records with ``delivery_id``, ``event_type``,
            ``status_code``, ``attempted_at``, and ``success``.
        """
        resp = self._transport.request(
            "GET", f"/api/v2/webhooks/{webhook_id}/deliveries"
        )
        return resp.data or []


class AsyncWebhooks:
    """Asynchronous webhook management operations.

    Same API surface as ``Webhooks`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        url: str,
        events: list[str],
        secret: str | None = None,
    ) -> dict[str, Any]:
        """Create a webhook. See ``Webhooks.create`` for details."""
        body: dict[str, Any] = {"url": url, "events": events}
        if secret is not None:
            body["secret"] = secret

        resp = await self._transport.request("POST", "/api/v2/webhooks", json=body)
        return resp.data or {}

    async def list(self) -> list[dict[str, Any]]:
        """List webhooks. See ``Webhooks.list`` for details."""
        resp = await self._transport.request("GET", "/api/v2/webhooks")
        return resp.data or []

    async def get(self, webhook_id: str) -> dict[str, Any]:
        """Get a webhook. See ``Webhooks.get`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/webhooks/{webhook_id}")
        return resp.data or {}

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook. See ``Webhooks.delete`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/webhooks/{webhook_id}")

    async def test(self, webhook_id: str) -> dict[str, Any]:
        """Test a webhook. See ``Webhooks.test`` for details."""
        resp = await self._transport.request(
            "POST", f"/api/v2/webhooks/{webhook_id}/test"
        )
        return resp.data or {}

    async def list_deliveries(self, webhook_id: str) -> list[dict[str, Any]]:
        """List webhook deliveries. See ``Webhooks.list_deliveries`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/webhooks/{webhook_id}/deliveries"
        )
        return resp.data or []
