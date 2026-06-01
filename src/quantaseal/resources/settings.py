"""Settings resource for tenant configuration management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Settings:
    """Synchronous tenant settings operations.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Read current settings
        config = qs.settings.get()

        # Update specific fields
        qs.settings.update({
            "mfa_required": True,
            "session_timeout_minutes": 60,
        })

        # List API keys
        keys = qs.settings.get_api_keys()

        # Rotate the signing key
        result = qs.settings.rotate_signing_key()
        print(result["new_key_id"])
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get(self) -> dict[str, Any]:
        """Retrieve current tenant settings.

        Returns:
            Dict with all configurable settings for the tenant, including
            ``mfa_required``, ``session_timeout_minutes``, ``allowed_ip_ranges``,
            ``notification_emails``, and more.
        """
        resp = self._transport.request("GET", "/api/v2/settings")
        return resp.data or {}

    def update(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Update one or more tenant settings.

        Args:
            updates: Dict of setting keys to update. Only the provided keys
                are modified; other settings remain unchanged.

        Returns:
            Dict of all settings after the update.
        """
        resp = self._transport.request("PATCH", "/api/v2/settings", json=updates)
        return resp.data or {}

    def get_api_keys(self) -> list[dict[str, Any]]:
        """List all API keys configured for the tenant.

        Returns:
            List of API key metadata dicts (key values are never returned after creation).
        """
        resp = self._transport.request("GET", "/api/v2/settings/api-keys")
        return resp.data or []

    def rotate_signing_key(self) -> dict[str, Any]:
        """Rotate the tenant's HMAC signing key.

        Generates a new signing key for webhook signatures and signed responses.
        The old key remains valid for a short grace period to allow in-flight
        verifications to complete.

        Returns:
            Dict with ``new_key_id``, ``old_key_id``, and ``grace_period_ends_at``.
        """
        resp = self._transport.request("POST", "/api/v2/settings/rotate-signing-key")
        return resp.data or {}


class AsyncSettings:
    """Asynchronous tenant settings operations.

    Same API surface as ``Settings`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get(self) -> dict[str, Any]:
        """Get tenant settings. See ``Settings.get`` for details."""
        resp = await self._transport.request("GET", "/api/v2/settings")
        return resp.data or {}

    async def update(self, updates: dict[str, Any]) -> dict[str, Any]:
        """Update tenant settings. See ``Settings.update`` for details."""
        resp = await self._transport.request("PATCH", "/api/v2/settings", json=updates)
        return resp.data or {}

    async def get_api_keys(self) -> list[dict[str, Any]]:
        """List API keys. See ``Settings.get_api_keys`` for details."""
        resp = await self._transport.request("GET", "/api/v2/settings/api-keys")
        return resp.data or []

    async def rotate_signing_key(self) -> dict[str, Any]:
        """Rotate signing key. See ``Settings.rotate_signing_key`` for details."""
        resp = await self._transport.request(
            "POST", "/api/v2/settings/rotate-signing-key"
        )
        return resp.data or {}
