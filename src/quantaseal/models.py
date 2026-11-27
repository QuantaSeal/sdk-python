"""Pydantic models for QuantaSeal API request/response types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# API response envelope
# ─────────────────────────────────────────────────────────────────────────────


class APIResponse(BaseModel):
    """Standard QuantaSeal API response wrapper."""

    success: bool
    data: Any = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Encryption / Decryption
# ─────────────────────────────────────────────────────────────────────────────


class EncryptResult(BaseModel):
    """Result of an encryption operation.

    Attributes:
        ciphertext: Base64-encoded ciphertext.
        encryption_metadata: Algorithm, key ID, nonce information.
        signature: Base64-encoded ML-DSA-65 signature over the ciphertext.
        envelope: Complete HybridCryptoEnvelope for decryption.
        request_id: Unique request identifier for audit trail.
    """

    ciphertext: str
    encryption_metadata: dict[str, Any]
    signature: str
    envelope: dict[str, Any]
    request_id: str | None = None

    @property
    def algorithm(self) -> str:
        """Encryption algorithm used."""
        return self.encryption_metadata.get("algorithm", "ML-KEM-768")

    @property
    def key_id(self) -> str | None:
        """Key ID used for encryption."""
        return self.encryption_metadata.get("key_id")


class DecryptResult(BaseModel):
    """Result of a decryption operation.

    Attributes:
        plaintext: Base64-encoded decrypted plaintext.
        signature_valid: Whether the signature was verified.
        encryption_metadata: Metadata from the envelope.
        request_id: Unique request identifier for audit trail.
    """

    plaintext: str
    signature_valid: bool
    encryption_metadata: dict[str, Any]
    request_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Digital Signatures
# ─────────────────────────────────────────────────────────────────────────────


class SignResult(BaseModel):
    """Result of a digital signature operation.

    Attributes:
        signature: Base64-encoded ML-DSA-65 signature.
        hmac_signature: Base64-encoded HMAC-SHA-512 signature.
        public_key: Base64-encoded public key for verification.
        algorithm: Algorithm used for signing.
        request_id: Unique request identifier for audit trail.
    """

    signature: str
    hmac_signature: str
    public_key: str
    algorithm: str
    request_id: str | None = None


class VerifyResult(BaseModel):
    """Result of a signature verification operation.

    Attributes:
        valid: Overall verification result.
        pqc_valid: Whether the ML-DSA-65 signature is valid.
        hmac_valid: Whether the HMAC-SHA-512 signature is valid.
        algorithm: Algorithm used for verification.
        verification_metadata: Additional verification context.
        request_id: Unique request identifier for audit trail.
    """

    valid: bool
    pqc_valid: bool
    hmac_valid: bool
    algorithm: str
    verification_metadata: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Vault
# ─────────────────────────────────────────────────────────────────────────────


class VaultEntry(BaseModel):
    """Vault entry metadata (no plaintext).

    Attributes:
        id: UUID of the vault entry.
        name: Human-readable credential name.
        credential_type: Type of credential (api_key, password, certificate, etc.).
        algorithm: Encryption algorithm used.
        is_active: Whether the entry is active (not deleted).
        created_at: ISO 8601 creation timestamp.
        last_accessed_at: ISO 8601 timestamp of last access (if any).
        ttl_expires_at: ISO 8601 TTL expiration timestamp (if set).
    """

    id: str
    name: str
    credential_type: str
    algorithm: str
    is_active: bool
    created_at: str
    last_accessed_at: str | None = None
    ttl_expires_at: str | None = None


class VaultUnsealResult(BaseModel):
    """Result of unsealing a vault entry.

    Attributes:
        plaintext: Decrypted credential data as a dictionary.
        last_accessed_at: ISO 8601 timestamp of last access.
        request_id: Unique request identifier for audit trail.
    """

    plaintext: dict[str, Any]
    last_accessed_at: str | None = None
    request_id: str | None = None


class VaultRotateResult(BaseModel):
    """Result of rotating a vault entry's encryption keys.

    Attributes:
        new_entry_id: UUID of the new entry (re-encrypted with fresh keys).
        old_entry_id: UUID of the old entry (now inactive).
        request_id: Unique request identifier for audit trail.
    """

    new_entry_id: str
    old_entry_id: str
    request_id: str | None = None
