"""QuantaSeal Python SDK client - sync and async."""

from __future__ import annotations

import os
from typing import Any

from quantaseal._transport import AsyncTransport, SyncTransport
from quantaseal.models import DecryptResult, EncryptResult, SignResult, VerifyResult
from quantaseal.resources.agent import Agent, AsyncAgent
from quantaseal.resources.audit import Audit, AsyncAudit
from quantaseal.resources.auth import AsyncAuth, Auth
from quantaseal.resources.billing import AsyncBilling, Billing
from quantaseal.resources.compliance import AsyncCompliance, Compliance
from quantaseal.resources.discovery import AsyncDiscovery, Discovery
from quantaseal.resources.encryption import AsyncEncryption, Encryption
from quantaseal.resources.files import AsyncFiles, Files
from quantaseal.resources.mappings import AsyncMappings, Mappings
from quantaseal.resources.metrics import AsyncMetrics, Metrics
from quantaseal.resources.mft import AsyncMFT, MFT
from quantaseal.resources.proxy import AsyncProxy, Proxy
from quantaseal.resources.security import AsyncSecurity, Security
from quantaseal.resources.settings import AsyncSettings, Settings
from quantaseal.resources.sync import AsyncSync, Sync
from quantaseal.resources.tokenize import AsyncTokenize, Tokenize
from quantaseal.resources.vault import AsyncVault, Vault
from quantaseal.resources.webhooks import AsyncWebhooks, Webhooks
from quantaseal.resources.workflows import AsyncWorkflows, Workflows

_DEFAULT_BASE_URL = "https://api.quantaseal.io"
_ENV_API_KEY = "QUANTASHIELD_API_KEY"
_ENV_BASE_URL = "QUANTASHIELD_BASE_URL"


class QuantaSeal:
    """Synchronous QuantaSeal client.

    Provides quantum-safe encryption, digital signatures, and credential vault
    management via the QuantaSeal REST API.

    Args:
        api_key: API key (``qs_live_...`` or ``qs_test_...``). Falls back to
            the ``QUANTASHIELD_API_KEY`` environment variable.
        base_url: API base URL. Falls back to ``QUANTASHIELD_BASE_URL`` env var
            or defaults to ``https://api.quantaseal.io``.
        timeout: Request timeout in seconds (default 30).
        max_retries: Maximum retry attempts for transient failures (default 3).
        headers: Additional HTTP headers to send with every request.

    Usage::

        from quantaseal import QuantaSeal

        qs = QuantaSeal(api_key="qs_test_abc123")

        # Encrypt data
        result = qs.encrypt(b"hello world")

        # Decrypt data
        decrypted = qs.decrypt(result.envelope)

        # Store a credential
        entry_id = qs.vault.seal("my-secret", "api_key", {"key": "value"})

        # Retrieve a credential
        creds = qs.vault.unseal(entry_id)

        # Clean up
        qs.close()
    """

    vault: Vault
    """Vault resource for credential lifecycle management."""

    auth: Auth
    """Authentication and MFA operations."""

    proxy: Proxy
    """Integration management and request forwarding."""

    compliance: Compliance
    """Compliance report generation and scoring."""

    billing: Billing
    """Plan management, usage, and invoices."""

    security: Security
    """API key management and emergency controls."""

    agent: Agent
    """AI agent conversation management."""

    tokenize: Tokenize
    """Data tokenization and detokenization."""

    mft: MFT
    """Managed File Transfer operations."""

    sync: Sync
    """Data synchronisation job management."""

    workflows: Workflows
    """Workflow automation management."""

    files: Files
    """Encrypted file storage and retrieval."""

    audit: Audit
    """Audit log access and export."""

    metrics: Metrics
    """Usage and performance statistics."""

    webhooks: Webhooks
    """Webhook endpoint management."""

    settings: Settings
    """Tenant configuration management."""

    discovery: Discovery
    """Schema and object discovery for integrations."""

    mappings: Mappings
    """Field mapping configuration."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
    ) -> None:
        resolved_key = api_key or os.environ.get(_ENV_API_KEY)
        if not resolved_key:
            raise ValueError(
                f"api_key must be provided or set via {_ENV_API_KEY} environment variable"
            )

        resolved_url = base_url or os.environ.get(_ENV_BASE_URL) or _DEFAULT_BASE_URL

        self._transport = SyncTransport(
            base_url=resolved_url,
            api_key=resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        self._encryption = Encryption(self._transport)
        self.vault = Vault(self._transport)
        self.auth = Auth(self._transport)
        self.proxy = Proxy(self._transport)
        self.compliance = Compliance(self._transport)
        self.billing = Billing(self._transport)
        self.security = Security(self._transport)
        self.agent = Agent(self._transport)
        self.tokenize = Tokenize(self._transport)
        self.mft = MFT(self._transport)
        self.sync = Sync(self._transport)
        self.workflows = Workflows(self._transport)
        self.files = Files(self._transport)
        self.audit = Audit(self._transport)
        self.metrics = Metrics(self._transport)
        self.webhooks = Webhooks(self._transport)
        self.settings = Settings(self._transport)
        self.discovery = Discovery(self._transport)
        self.mappings = Mappings(self._transport)

    # ── Convenience methods (delegate to Encryption resource) ────────────

    def encrypt(
        self,
        plaintext: bytes,
        *,
        algorithm: str = "ML-KEM-768",
        encryption_context: dict[str, Any] | None = None,
    ) -> EncryptResult:
        """Encrypt data using ML-KEM-768 + AES-256-GCM + ML-DSA-65.

        This is a convenience wrapper around ``qs.encryption.encrypt()``.

        Args:
            plaintext: Raw bytes to encrypt.
            algorithm: Encryption algorithm (default ``ML-KEM-768``).
            encryption_context: Optional AAD for authenticated encryption.

        Returns:
            EncryptResult with ciphertext, signature, and envelope.
        """
        return self._encryption.encrypt(
            plaintext,
            algorithm=algorithm,
            encryption_context=encryption_context,
        )

    def decrypt(
        self,
        envelope: dict[str, Any],
        *,
        verify_signature: bool = True,
    ) -> DecryptResult:
        """Decrypt data using a HybridCryptoEnvelope.

        Args:
            envelope: Complete envelope from a previous ``encrypt()`` call.
            verify_signature: Verify signature before decryption (default ``True``).

        Returns:
            DecryptResult with base64-encoded plaintext.
        """
        return self._encryption.decrypt(envelope, verify_signature=verify_signature)

    def sign(
        self,
        data: bytes,
        *,
        algorithm: str = "ML-DSA-65",
    ) -> SignResult:
        """Sign data with ML-DSA-65 + HMAC-SHA-512.

        Args:
            data: Raw bytes to sign.
            algorithm: Signature algorithm (default ``ML-DSA-65``).

        Returns:
            SignResult with signatures and public key.
        """
        return self._encryption.sign(data, algorithm=algorithm)

    def verify(
        self,
        data: bytes,
        signature: str,
        hmac_signature: str,
        public_key: str,
        *,
        hmac_secret: str | None = None,
    ) -> VerifyResult:
        """Verify an ML-DSA-65 + HMAC-SHA-512 signature.

        Args:
            data: Original bytes that were signed.
            signature: Base64-encoded ML-DSA-65 signature.
            hmac_signature: Base64-encoded HMAC-SHA-512 signature.
            public_key: Base64-encoded public key.
            hmac_secret: Optional HMAC secret (uses tenant key if omitted).

        Returns:
            VerifyResult with per-algorithm validity flags.
        """
        return self._encryption.verify(
            data,
            signature,
            hmac_signature,
            public_key,
            hmac_secret=hmac_secret,
        )

    @property
    def encryption(self) -> Encryption:
        """Access the full Encryption resource directly."""
        return self._encryption

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._transport.close()

    def __enter__(self) -> QuantaSeal:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"QuantaSeal(base_url={self._transport._base_url!r})"


class AsyncQuantaSeal:
    """Asynchronous QuantaSeal client.

    Same API surface as ``QuantaSeal`` but all operations are ``async``.

    Usage::

        from quantaseal import AsyncQuantaSeal

        async with AsyncQuantaSeal(api_key="qs_test_abc123") as qs:
            result = await qs.encrypt(b"hello world")
            decrypted = await qs.decrypt(result.envelope)

            entry_id = await qs.vault.seal("secret", "api_key", {"k": "v"})
            creds = await qs.vault.unseal(entry_id)
    """

    vault: AsyncVault
    """Vault resource for credential lifecycle management."""

    auth: AsyncAuth
    """Authentication and MFA operations."""

    proxy: AsyncProxy
    """Integration management and request forwarding."""

    compliance: AsyncCompliance
    """Compliance report generation and scoring."""

    billing: AsyncBilling
    """Plan management, usage, and invoices."""

    security: AsyncSecurity
    """API key management and emergency controls."""

    agent: AsyncAgent
    """AI agent conversation management."""

    tokenize: AsyncTokenize
    """Data tokenization and detokenization."""

    mft: AsyncMFT
    """Managed File Transfer operations."""

    sync: AsyncSync
    """Data synchronisation job management."""

    workflows: AsyncWorkflows
    """Workflow automation management."""

    files: AsyncFiles
    """Encrypted file storage and retrieval."""

    audit: AsyncAudit
    """Audit log access and export."""

    metrics: AsyncMetrics
    """Usage and performance statistics."""

    webhooks: AsyncWebhooks
    """Webhook endpoint management."""

    settings: AsyncSettings
    """Tenant configuration management."""

    discovery: AsyncDiscovery
    """Schema and object discovery for integrations."""

    mappings: AsyncMappings
    """Field mapping configuration."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
    ) -> None:
        resolved_key = api_key or os.environ.get(_ENV_API_KEY)
        if not resolved_key:
            raise ValueError(
                f"api_key must be provided or set via {_ENV_API_KEY} environment variable"
            )

        resolved_url = base_url or os.environ.get(_ENV_BASE_URL) or _DEFAULT_BASE_URL

        self._transport = AsyncTransport(
            base_url=resolved_url,
            api_key=resolved_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )
        self._encryption = AsyncEncryption(self._transport)
        self.vault = AsyncVault(self._transport)
        self.auth = AsyncAuth(self._transport)
        self.proxy = AsyncProxy(self._transport)
        self.compliance = AsyncCompliance(self._transport)
        self.billing = AsyncBilling(self._transport)
        self.security = AsyncSecurity(self._transport)
        self.agent = AsyncAgent(self._transport)
        self.tokenize = AsyncTokenize(self._transport)
        self.mft = AsyncMFT(self._transport)
        self.sync = AsyncSync(self._transport)
        self.workflows = AsyncWorkflows(self._transport)
        self.files = AsyncFiles(self._transport)
        self.audit = AsyncAudit(self._transport)
        self.metrics = AsyncMetrics(self._transport)
        self.webhooks = AsyncWebhooks(self._transport)
        self.settings = AsyncSettings(self._transport)
        self.discovery = AsyncDiscovery(self._transport)
        self.mappings = AsyncMappings(self._transport)

    # ── Convenience methods ──────────────────────────────────────────────

    async def encrypt(
        self,
        plaintext: bytes,
        *,
        algorithm: str = "ML-KEM-768",
        encryption_context: dict[str, Any] | None = None,
    ) -> EncryptResult:
        """Encrypt data. See ``QuantaSeal.encrypt`` for details."""
        return await self._encryption.encrypt(
            plaintext,
            algorithm=algorithm,
            encryption_context=encryption_context,
        )

    async def decrypt(
        self,
        envelope: dict[str, Any],
        *,
        verify_signature: bool = True,
    ) -> DecryptResult:
        """Decrypt data. See ``QuantaSeal.decrypt`` for details."""
        return await self._encryption.decrypt(envelope, verify_signature=verify_signature)

    async def sign(
        self,
        data: bytes,
        *,
        algorithm: str = "ML-DSA-65",
    ) -> SignResult:
        """Sign data. See ``QuantaSeal.sign`` for details."""
        return await self._encryption.sign(data, algorithm=algorithm)

    async def verify(
        self,
        data: bytes,
        signature: str,
        hmac_signature: str,
        public_key: str,
        *,
        hmac_secret: str | None = None,
    ) -> VerifyResult:
        """Verify a signature. See ``QuantaSeal.verify`` for details."""
        return await self._encryption.verify(
            data,
            signature,
            hmac_signature,
            public_key,
            hmac_secret=hmac_secret,
        )

    @property
    def encryption(self) -> AsyncEncryption:
        """Access the full Encryption resource directly."""
        return self._encryption

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._transport.close()

    async def __aenter__(self) -> AsyncQuantaSeal:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncQuantaSeal(base_url={self._transport._base_url!r})"
