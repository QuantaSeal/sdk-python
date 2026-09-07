"""Security resource for API key management and emergency controls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Security:
    """Synchronous security operations - API keys, revocation, emergency lockdown.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # List current API keys
        keys = qs.security.list_api_keys()

        # Create a scoped key
        new_key = qs.security.create_api_key(
            name="ci-pipeline",
            scopes=["encryption:read", "encryption:write"],
        )
        print(new_key["api_key"])  # store securely - shown only once

        # Revoke a key
        qs.security.revoke_api_key(new_key["id"])

        # Emergency lockdown
        qs.security.emergency_lockdown("Suspected key compromise")
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def revoke_integration(self, integration_id: str, hmac_signature: str) -> dict[str, Any]:
        """Revoke an integration using an HMAC-signed revocation request.

        Args:
            integration_id: UUID of the integration to revoke.
            hmac_signature: HMAC-SHA-512 signature over the integration ID.

        Returns:
            Dict with ``revoked`` bool and ``revoked_at`` timestamp.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/security/revoke-integration",
            json={"integration_id": integration_id, "hmac_signature": hmac_signature},
        )
        return resp.data or {}

    def list_api_keys(self) -> list[dict[str, Any]]:
        """List all API keys for the tenant.

        Returns:
            List of API key metadata dicts (key values are never returned).
        """
        resp = self._transport.request("GET", "/api/v2/security/api-keys")
        return resp.data or []

    def create_api_key(
        self,
        name: str,
        scopes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new API key with optional scope restrictions.

        Args:
            name: Human-readable name for the key (e.g. ``ci-pipeline``).
            scopes: List of permission scopes. Omit for full access.

        Returns:
            Dict with ``id``, ``api_key`` (plaintext - store immediately),
            ``name``, ``scopes``, and ``created_at``.
        """
        body: dict[str, Any] = {"name": name}
        if scopes is not None:
            body["scopes"] = scopes

        resp = self._transport.request("POST", "/api/v2/security/api-keys", json=body)
        return resp.data or {}

    def revoke_api_key(self, key_id: str) -> None:
        """Permanently revoke an API key.

        Args:
            key_id: UUID of the API key to revoke.

        Raises:
            NotFoundError: If the key does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/security/api-keys/{key_id}")

    def emergency_lockdown(self, reason: str) -> dict[str, Any]:
        """Activate emergency lockdown - immediately blocks all API access.

        All active sessions, tokens, and API keys are invalidated. A manual
        unlock via the dashboard is required to restore access.

        Args:
            reason: Human-readable reason for the lockdown (logged to audit trail).

        Returns:
            Dict with ``locked``, ``locked_at``, and ``unlock_instructions``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/security/emergency-lockdown",
            json={"reason": reason},
        )
        return resp.data or {}


class AsyncSecurity:
    """Asynchronous security operations.

    Same API surface as ``Security`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def revoke_integration(
        self, integration_id: str, hmac_signature: str
    ) -> dict[str, Any]:
        """Revoke an integration. See ``Security.revoke_integration`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/security/revoke-integration",
            json={"integration_id": integration_id, "hmac_signature": hmac_signature},
        )
        return resp.data or {}

    async def list_api_keys(self) -> list[dict[str, Any]]:
        """List API keys. See ``Security.list_api_keys`` for details."""
        resp = await self._transport.request("GET", "/api/v2/security/api-keys")
        return resp.data or []

    async def create_api_key(
        self,
        name: str,
        scopes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create an API key. See ``Security.create_api_key`` for details."""
        body: dict[str, Any] = {"name": name}
        if scopes is not None:
            body["scopes"] = scopes

        resp = await self._transport.request("POST", "/api/v2/security/api-keys", json=body)
        return resp.data or {}

    async def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key. See ``Security.revoke_api_key`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/security/api-keys/{key_id}")

    async def emergency_lockdown(self, reason: str) -> dict[str, Any]:
        """Emergency lockdown. See ``Security.emergency_lockdown`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/security/emergency-lockdown",
            json={"reason": reason},
        )
        return resp.data or {}
