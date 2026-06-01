"""Discovery resource for schema and object discovery on external integrations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Discovery:
    """Synchronous schema and object discovery operations.

    Discovery introspects connected integrations to enumerate available
    objects and their field definitions, enabling dynamic field mapping.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Discover the full schema
        schema = qs.discovery.discover_schema("int_abc123")

        # List available objects
        objects = qs.discovery.list_objects("int_abc123")

        # Get fields for a specific object
        fields = qs.discovery.get_object_fields("int_abc123", "Account")
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def discover_schema(self, integration_id: str) -> dict[str, Any]:
        """Discover the full schema of an integration's target system.

        Introspects the remote system and returns a structured representation
        of all available objects and their fields.

        Args:
            integration_id: UUID of the integration to inspect.

        Returns:
            Dict with ``objects`` (list of object names) and ``schema_version``.

        Raises:
            NotFoundError: If the integration does not exist.
        """
        resp = self._transport.request(
            "POST", f"/api/v2/discovery/{integration_id}/schema"
        )
        return resp.data or {}

    def list_objects(self, integration_id: str) -> list[dict[str, Any]]:
        """List available objects in an integration's target system.

        Args:
            integration_id: UUID of the integration.

        Returns:
            List of object descriptor dicts with ``name``, ``label``,
            ``queryable``, and ``createable`` flags.
        """
        resp = self._transport.request(
            "GET", f"/api/v2/discovery/{integration_id}/objects"
        )
        return resp.data or []

    def get_object_fields(
        self, integration_id: str, object_name: str
    ) -> list[dict[str, Any]]:
        """Get field definitions for a specific object.

        Args:
            integration_id: UUID of the integration.
            object_name: API name of the object (e.g. ``Account``, ``contacts``).

        Returns:
            List of field descriptor dicts with ``name``, ``label``, ``type``,
            ``required``, and ``length`` (where applicable).

        Raises:
            NotFoundError: If the object does not exist in the schema.
        """
        resp = self._transport.request(
            "GET",
            f"/api/v2/discovery/{integration_id}/objects/{object_name}/fields",
        )
        return resp.data or []


class AsyncDiscovery:
    """Asynchronous discovery operations.

    Same API surface as ``Discovery`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def discover_schema(self, integration_id: str) -> dict[str, Any]:
        """Discover schema. See ``Discovery.discover_schema`` for details."""
        resp = await self._transport.request(
            "POST", f"/api/v2/discovery/{integration_id}/schema"
        )
        return resp.data or {}

    async def list_objects(self, integration_id: str) -> list[dict[str, Any]]:
        """List objects. See ``Discovery.list_objects`` for details."""
        resp = await self._transport.request(
            "GET", f"/api/v2/discovery/{integration_id}/objects"
        )
        return resp.data or []

    async def get_object_fields(
        self, integration_id: str, object_name: str
    ) -> list[dict[str, Any]]:
        """Get object fields. See ``Discovery.get_object_fields`` for details."""
        resp = await self._transport.request(
            "GET",
            f"/api/v2/discovery/{integration_id}/objects/{object_name}/fields",
        )
        return resp.data or []
