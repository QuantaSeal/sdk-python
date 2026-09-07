"""QuantaSeal Python SDK - Universal Quantum-Safe Security Middleware.

Usage:
    from quantaseal import QuantaSeal

    qs = QuantaSeal(base_url="https://api.quantaseal.io", api_key="qs_live_...")

    # Encrypt
    result = qs.encrypt(b"secret data")

    # Decrypt
    plaintext = qs.decrypt(result.envelope)

    # Sign
    signed = qs.sign(b"message to sign")

    # Verify
    valid = qs.verify(b"message to sign", signed.signature, signed.public_key)

    # Vault
    entry_id = qs.vault.seal("aws-credentials", {"access_key": "...", "secret_key": "..."})
    creds = qs.vault.unseal(entry_id)

    # Auth
    tokens = qs.auth.login("user@example.com", "password")

    # Compliance
    report = qs.compliance.generate_report("SOC2")

    # And many more resources: proxy, billing, security, agent, tokenize,
    # mft, sync, workflows, files, audit, metrics, webhooks, settings,
    # discovery, mappings.

Async usage:
    from quantaseal import AsyncQuantaSeal

    async with AsyncQuantaSeal(base_url="...", api_key="...") as qs:
        result = await qs.encrypt(b"secret data")
"""

from quantaseal._version import __version__
from quantaseal.client import AsyncQuantaSeal, QuantaSeal
from quantaseal.exceptions import (
    AuthenticationError,
    QuantaSealError,
    RateLimitError,
    ServerError,
    ValidationError,
    VaultError,
)
from quantaseal.models import (
    DecryptResult,
    EncryptResult,
    SignResult,
    VerifyResult,
    VaultEntry,
    VaultRotateResult,
    VaultUnsealResult,
)
from quantaseal.resources.agent import Agent, AsyncAgent
from quantaseal.resources.audit import AsyncAudit, Audit
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

__all__ = [
    # Clients
    "QuantaSeal",
    "AsyncQuantaSeal",
    # Models
    "EncryptResult",
    "DecryptResult",
    "SignResult",
    "VerifyResult",
    "VaultEntry",
    "VaultUnsealResult",
    "VaultRotateResult",
    # Exceptions
    "QuantaSealError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "VaultError",
    # Resource classes (sync)
    "Encryption",
    "Vault",
    "Auth",
    "Proxy",
    "Compliance",
    "Billing",
    "Security",
    "Agent",
    "Tokenize",
    "MFT",
    "Sync",
    "Workflows",
    "Files",
    "Audit",
    "Metrics",
    "Webhooks",
    "Settings",
    "Discovery",
    "Mappings",
    # Resource classes (async)
    "AsyncEncryption",
    "AsyncVault",
    "AsyncAuth",
    "AsyncProxy",
    "AsyncCompliance",
    "AsyncBilling",
    "AsyncSecurity",
    "AsyncAgent",
    "AsyncTokenize",
    "AsyncMFT",
    "AsyncSync",
    "AsyncWorkflows",
    "AsyncFiles",
    "AsyncAudit",
    "AsyncMetrics",
    "AsyncWebhooks",
    "AsyncSettings",
    "AsyncDiscovery",
    "AsyncMappings",
    # Version
    "__version__",
]
