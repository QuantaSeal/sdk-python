"""Mappings resource for field mapping configuration between integrations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Mappings:
    """Synchronous field mapping management.

    Mappings define how fields on a source object in an integration correspond
    to fields on a target object, enabling data translation during sync jobs.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Create a field mapping
        mapping = qs.mappings.create(
            integration_id="int_abc123",
            source_object="Contact",
            target_object="contacts",
            field_mappings=[
                {"source_field": "FirstName", "target_field": "first_name"},
                {"source_field": "Email", "target_field": "email_address"},
            ],
        )

        # List mappings for an integration
        all_mappings = qs.mappings.list("int_abc123")

        # Update a mapping
        qs.mappings.update(mapping["id"], {"field_mappings": [...]})
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create(
        self,
        integration_id: str,
        source_object: str,
        target_object: str,
        field_mappings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a new field mapping.

        Args:
            integration_id: UUID of the integration this mapping belongs to.
            source_object: API name of the source object.
            target_object: API name of the target object.
            field_mappings: List of field mapping dicts, each with
                ``source_field`` and ``target_field`` keys (and optional
                ``transform`` for value transformation).

        Returns:
            Dict with ``id``, ``integration_id``, ``source_object``,
            ``target_object``, ``field_mappings``, and ``created_at``.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/mappings",
            json={
                "integration_id": integration_id,
                "source_object": source_object,
                "target_object": target_object,
                "field_mappings": field_mappings,
            },
        )
        return resp.data or {}

    def list(self, integration_id: str) -> list[dict[str, Any]]:
        """List all field mappings for an integration.

        Args:
            integration_id: UUID of the integration.

        Returns:
            List of mapping metadata dicts.
        """
        resp = self._transport.request(
            "GET",
            "/api/v2/mappings",
            params={"integration_id": integration_id},
        )
        return resp.data or []

    def get(self, mapping_id: str) -> dict[str, Any]:
        """Get a field mapping by ID.

        Args:
            mapping_id: UUID of the mapping.

        Returns:
            Full mapping definition dict.

        Raises:
            NotFoundError: If the mapping does not exist.
        """
        resp = self._transport.request("GET", f"/api/v2/mappings/{mapping_id}")
        return resp.data or {}

    def update(self, mapping_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a field mapping.

        Args:
            mapping_id: UUID of the mapping to update.
            updates: Dict of fields to update (e.g. ``field_mappings``,
                ``source_object``, ``target_object``).

        Returns:
            Updated mapping dict.

        Raises:
            NotFoundError: If the mapping does not exist.
        """
        resp = self._transport.request(
            "PATCH", f"/api/v2/mappings/{mapping_id}", json=updates
        )
        return resp.data or {}

    def delete(self, mapping_id: str) -> None:
        """Delete a field mapping.

        Args:
            mapping_id: UUID of the mapping to delete.

        Raises:
            NotFoundError: If the mapping does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/mappings/{mapping_id}")


class AsyncMappings:
    """Asynchronous field mapping operations.

    Same API surface as ``Mappings`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        integration_id: str,
        source_object: str,
        target_object: str,
        field_mappings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a mapping. See ``Mappings.create`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/mappings",
            json={
                "integration_id": integration_id,
                "source_object": source_object,
                "target_object": target_object,
                "field_mappings": field_mappings,
            },
        )
        return resp.data or {}

    async def list(self, integration_id: str) -> list[dict[str, Any]]:
        """List mappings. See ``Mappings.list`` for details."""
        resp = await self._transport.request(
            "GET",
            "/api/v2/mappings",
            params={"integration_id": integration_id},
        )
        return resp.data or []

    async def get(self, mapping_id: str) -> dict[str, Any]:
        """Get a mapping. See ``Mappings.get`` for details."""
        resp = await self._transport.request("GET", f"/api/v2/mappings/{mapping_id}")
        return resp.data or {}

    async def update(self, mapping_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a mapping. See ``Mappings.update`` for details."""
        resp = await self._transport.request(
            "PATCH", f"/api/v2/mappings/{mapping_id}", json=updates
        )
        return resp.data or {}

    async def delete(self, mapping_id: str) -> None:
        """Delete a mapping. See ``Mappings.delete`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/mappings/{mapping_id}")
