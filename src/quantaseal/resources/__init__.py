"""Resource sub-packages for QuantaSeal SDK."""

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
    # Sync
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
    # Async
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
]
