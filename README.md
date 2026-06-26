# QuantaSeal Python SDK

[![PyPI version](https://img.shields.io/pypi/v/quantaseal.svg)](https://pypi.org/project/quantaseal/)
[![Python](https://img.shields.io/pypi/pyversions/quantaseal.svg)](https://pypi.org/project/quantaseal/)
[![License](https://img.shields.io/pypi/l/quantaseal.svg)](https://github.com/quantaseal/quantaseal-python/blob/main/LICENSE)

Python SDK for **QuantaSeal** - Universal Quantum-Safe Security Middleware.

Provides a clean, typed interface to:
- **Encrypt / Decrypt** data with ML-KEM-768 + AES-256-GCM (post-quantum key encapsulation)
- **Sign / Verify** payloads with ML-DSA-65 + HMAC-SHA-512 (post-quantum digital signatures)
- **Vault** management - seal, unseal, rotate, list, and delete credentials with 3-layer PQC encryption

## Installation

```bash
pip install quantaseal
```

For async support with HTTP/2:

```bash
pip install "quantaseal[async]"
```

## Quick Start

### Encrypt & Decrypt

```python
from quantaseal import QuantaSeal

qs = QuantaSeal(api_key="qs_live_...")

# Encrypt
result = qs.encrypt(b"sensitive data")
print(result.ciphertext)    # base64-encoded ciphertext
print(result.algorithm)     # "ML-KEM-768"

# Decrypt using the envelope
decrypted = qs.decrypt(result.envelope)
print(decrypted.plaintext)  # base64-encoded original
print(decrypted.signature_valid)  # True
```

### Sign & Verify

```python
# Sign a document
signed = qs.sign(b"document content")
print(signed.signature)     # ML-DSA-65 signature
print(signed.public_key)    # for verification

# Verify
verified = qs.verify(
    data=b"document content",
    signature=signed.signature,
    hmac_signature=signed.hmac_signature,
    public_key=signed.public_key,
)
print(verified.valid)       # True
print(verified.pqc_valid)   # True (ML-DSA-65)
print(verified.hmac_valid)  # True (HMAC-SHA-512)
```

### Credential Vault

```python
# Seal (encrypt + store) a credential
entry_id = qs.vault.seal(
    name="aws-production-keys",
    credential_type="api_key",
    plaintext={
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    ttl_days=90,
    metadata={"environment": "production", "region": "us-east-1"},
)

# Unseal (decrypt + retrieve)
creds = qs.vault.unseal(entry_id)
print(creds.plaintext["access_key"])

# List all stored credentials (metadata only)
entries = qs.vault.list()
for entry in entries:
    print(f"{entry.name} ({entry.credential_type}) - active: {entry.is_active}")

# Rotate encryption keys
rotated = qs.vault.rotate(entry_id)
print(f"New entry: {rotated.new_entry_id}")

# Delete
qs.vault.delete(rotated.new_entry_id)
```

### Async Usage

```python
import asyncio
from quantaseal import AsyncQuantaSeal

async def main():
    async with AsyncQuantaSeal(api_key="qs_live_...") as qs:
        # All methods are async
        result = await qs.encrypt(b"async encryption")
        decrypted = await qs.decrypt(result.envelope)

        entry_id = await qs.vault.seal(
            name="db-password",
            credential_type="password",
            plaintext={"password": "s3cret!"},
        )
        creds = await qs.vault.unseal(entry_id)

asyncio.run(main())
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QUANTASHIELD_API_KEY` | API key (fallback if not passed to constructor) | - |
| `QUANTASHIELD_BASE_URL` | API base URL | `https://api.quantaseal.io` |

### Constructor Options

```python
qs = QuantaSeal(
    api_key="qs_live_...",           # Required (or set QUANTASHIELD_API_KEY)
    base_url="https://...",          # Optional: custom API URL
    timeout=30.0,                     # Request timeout in seconds
    max_retries=3,                    # Retries for transient failures (429, 5xx)
    headers={"X-Custom": "value"},   # Additional headers
)
```

## Error Handling

The SDK provides a typed exception hierarchy:

```python
from quantaseal import QuantaSeal
from quantaseal.exceptions import (
    QuantaSealError,    # Base exception
    AuthenticationError,  # 401/403 - invalid API key
    ValidationError,      # 400/422 - bad request data
    NotFoundError,        # 404 - resource not found
    RateLimitError,       # 429 - rate limit exceeded
    VaultError,           # 410 - vault entry expired
    ServerError,          # 5xx - transient server error
    ConnectionError,      # Network connectivity failure
    TimeoutError,         # Request timeout
)

qs = QuantaSeal(api_key="qs_test_...")

try:
    result = qs.encrypt(b"data")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    print(f"Request ID: {e.request_id}")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after}s")
except ServerError as e:
    print(f"Server error (will auto-retry): {e.status_code}")
except QuantaSealError as e:
    print(f"SDK error: {e}")
```

### Automatic Retries

The SDK automatically retries on:
- **429** Too Many Requests (respects `Retry-After` header)
- **500, 502, 503, 504** Server errors

Retries use exponential backoff: 0.5s → 1s → 2s → ...

## Supported Algorithms

| Operation | Algorithm | Standard |
|-----------|-----------|----------|
| Encryption | ML-KEM-768 + AES-256-GCM | NIST FIPS 203 |
| Signing | ML-DSA-65 + HMAC-SHA-512 | NIST FIPS 204 |

## API Reference

### `QuantaSeal` / `AsyncQuantaSeal`

| Method | Description |
|--------|-------------|
| `encrypt(plaintext, *, algorithm, encryption_context)` | Encrypt raw bytes |
| `decrypt(envelope, *, verify_signature)` | Decrypt using HybridCryptoEnvelope |
| `sign(data, *, algorithm)` | Sign raw bytes |
| `verify(data, signature, hmac_signature, public_key)` | Verify signature |
| `vault.seal(name, credential_type, plaintext, *, ttl_days, metadata)` | Store credential |
| `vault.unseal(entry_id)` | Retrieve credential |
| `vault.rotate(entry_id)` | Rotate encryption keys |
| `vault.list(*, include_inactive)` | List entries (metadata only) |
| `vault.delete(entry_id)` | Soft-delete entry |
| `close()` | Close HTTP connection pool |

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/quantaseal/quantaseal-python.git
cd quantaseal-python
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=quantaseal --cov-report=html

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.
