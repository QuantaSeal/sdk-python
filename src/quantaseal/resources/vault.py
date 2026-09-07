"""Vault resource for credential lifecycle management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from quantaseal.models import VaultEntry, VaultRotateResult, VaultUnsealResult

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Vault:
    """Synchronous vault operations - seal, unseal, rotate, list, delete.

    Usage::

        qs = QuantaSeal(...)

        # Store a credential
        entry_id = qs.vault.seal(
            name="aws-prod-keys",
            credential_type="api_key",
            plaintext={"access_key": "AKIA...", "secret_key": "wJal..."},
            ttl_days=90,
        )

        # Retrieve a credential
        result = qs.vault.unseal(entry_id)
        print(result.plaintext)

        # List all entries (metadata only)
        entries = qs.vault.list()

        # Rotate encryption keys
        rotated = qs.vault.rotate(entry_id)
        print(rotated.new_entry_id)

        # Delete
        qs.vault.delete(entry_id)
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def seal(
        self,
        name: str,
        credential_type: str,
        plaintext: dict[str, Any],
        *,
        ttl_days: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Seal (encrypt and store) a credential in the vault.

        Args:
            name: Human-readable name for the credential.
            credential_type: Type of credential. One of:
                ``api_key``, ``password``, ``certificate``, ``ssh_key``,
                ``oauth_token``, ``database``, ``generic``.
            plaintext: Credential data as a dictionary.
            ttl_days: Optional time-to-live in days (1–365). ``None`` = no expiry.
            metadata: Optional metadata dictionary.

        Returns:
            UUID string of the sealed vault entry.

        Raises:
            ValidationError: If credential_type is invalid or plaintext is empty.
            AuthenticationError: If the API key is invalid.
        """
        body: dict[str, Any] = {
            "name": name,
            "credential_type": credential_type,
            "plaintext": plaintext,
        }
        if ttl_days is not None:
            body["ttl_days"] = ttl_days
        if metadata is not None:
            body["metadata"] = metadata

        resp = self._transport.request("POST", "/api/v2/vault/seal", json=body)
        return str(resp.data)

    def unseal(self, entry_id: str) -> VaultUnsealResult:
        """Unseal (decrypt and retrieve) a credential from the vault.

        Args:
            entry_id: UUID of the vault entry to unseal.

        Returns:
            VaultUnsealResult with decrypted plaintext.

        Raises:
            NotFoundError: If the entry does not exist.
            VaultError: If the entry has expired (410 Gone).
        """
        resp = self._transport.request("POST", f"/api/v2/vault/unseal/{entry_id}")
        data = resp.data or {}
        return VaultUnsealResult(
            plaintext=data.get("plaintext", {}),
            last_accessed_at=data.get("last_accessed_at"),
            request_id=resp.meta.get("request_id"),
        )

    def rotate(self, entry_id: str) -> VaultRotateResult:
        """Rotate encryption keys for a vault entry.

        The credential is decrypted with the current keys and re-encrypted
        with fresh keys. The old entry becomes inactive.

        Args:
            entry_id: UUID of the vault entry to rotate.

        Returns:
            VaultRotateResult with old and new entry IDs.
        """
        resp = self._transport.request("POST", f"/api/v2/vault/rotate/{entry_id}")
        data = resp.data or {}
        return VaultRotateResult(
            new_entry_id=data.get("new_entry_id", ""),
            old_entry_id=data.get("old_entry_id", ""),
            request_id=resp.meta.get("request_id"),
        )

    def list(self, *, include_inactive: bool = False) -> list[VaultEntry]:
        """List all vault entries (metadata only - no plaintext).

        Args:
            include_inactive: Include soft-deleted entries.

        Returns:
            List of VaultEntry metadata objects.
        """
        params: dict[str, Any] = {}
        if include_inactive:
            params["include_inactive"] = "true"

        resp = self._transport.request("GET", "/api/v2/vault/entries", params=params)
        entries_data = resp.data or []
        return [VaultEntry.model_validate(e) for e in entries_data]

    def delete(self, entry_id: str) -> None:
        """Soft-delete a vault entry.

        Args:
            entry_id: UUID of the vault entry to delete.

        Raises:
            NotFoundError: If the entry does not exist.
        """
        self._transport.request_raw("DELETE", f"/api/v2/vault/entries/{entry_id}")


class AsyncVault:
    """Asynchronous vault operations - seal, unseal, rotate, list, delete.

    Usage::

        async with AsyncQuantaSeal(...) as qs:
            entry_id = await qs.vault.seal(
                name="aws-prod-keys",
                credential_type="api_key",
                plaintext={"access_key": "AKIA...", "secret_key": "wJal..."},
            )
            result = await qs.vault.unseal(entry_id)
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def seal(
        self,
        name: str,
        credential_type: str,
        plaintext: dict[str, Any],
        *,
        ttl_days: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Seal (encrypt and store) a credential. See ``Vault.seal`` for details."""
        body: dict[str, Any] = {
            "name": name,
            "credential_type": credential_type,
            "plaintext": plaintext,
        }
        if ttl_days is not None:
            body["ttl_days"] = ttl_days
        if metadata is not None:
            body["metadata"] = metadata

        resp = await self._transport.request("POST", "/api/v2/vault/seal", json=body)
        return str(resp.data)

    async def unseal(self, entry_id: str) -> VaultUnsealResult:
        """Unseal a credential. See ``Vault.unseal`` for details."""
        resp = await self._transport.request("POST", f"/api/v2/vault/unseal/{entry_id}")
        data = resp.data or {}
        return VaultUnsealResult(
            plaintext=data.get("plaintext", {}),
            last_accessed_at=data.get("last_accessed_at"),
            request_id=resp.meta.get("request_id"),
        )

    async def rotate(self, entry_id: str) -> VaultRotateResult:
        """Rotate encryption keys. See ``Vault.rotate`` for details."""
        resp = await self._transport.request("POST", f"/api/v2/vault/rotate/{entry_id}")
        data = resp.data or {}
        return VaultRotateResult(
            new_entry_id=data.get("new_entry_id", ""),
            old_entry_id=data.get("old_entry_id", ""),
            request_id=resp.meta.get("request_id"),
        )

    async def list(self, *, include_inactive: bool = False) -> list[VaultEntry]:
        """List vault entries. See ``Vault.list`` for details."""
        params: dict[str, Any] = {}
        if include_inactive:
            params["include_inactive"] = "true"

        resp = await self._transport.request("GET", "/api/v2/vault/entries", params=params)
        entries_data = resp.data or []
        return [VaultEntry.model_validate(e) for e in entries_data]

    async def delete(self, entry_id: str) -> None:
        """Delete a vault entry. See ``Vault.delete`` for details."""
        await self._transport.request_raw("DELETE", f"/api/v2/vault/entries/{entry_id}")
