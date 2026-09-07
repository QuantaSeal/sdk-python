"""Encryption resource for quantum-safe encrypt/decrypt/sign/verify operations."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

from quantaseal.models import DecryptResult, EncryptResult, SignResult, VerifyResult

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Encryption:
    """Synchronous quantum-safe encryption operations.

    Uses ML-KEM-768 + AES-256-GCM for encryption and ML-DSA-65 for digital
    signatures. All cryptographic operations happen server-side - the SDK
    handles base64 encoding/decoding and envelope management.

    Usage::

        qs = QuantaSeal(...)

        # Encrypt raw bytes
        result = qs.encrypt(b"sensitive data")
        print(result.ciphertext)  # base64-encoded

        # Decrypt using the envelope from encryption
        decrypted = qs.decrypt(result.envelope)
        print(decrypted.plaintext)  # base64-encoded original

        # Sign data
        signed = qs.sign(b"document content")

        # Verify signature
        verified = qs.verify(
            data=b"document content",
            signature=signed.signature,
            hmac_signature=signed.hmac_signature,
            public_key=signed.public_key,
        )
        print(verified.valid)  # True
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def encrypt(
        self,
        plaintext: bytes,
        *,
        algorithm: str = "ML-KEM-768",
        encryption_context: dict[str, Any] | None = None,
    ) -> EncryptResult:
        """Encrypt data using ML-KEM-768 + AES-256-GCM + ML-DSA-65.

        Args:
            plaintext: Raw bytes to encrypt.
            algorithm: Encryption algorithm (default ``ML-KEM-768``).
            encryption_context: Optional additional authenticated data (AAD).

        Returns:
            EncryptResult with ciphertext, signature, and full envelope.
        """
        body: dict[str, Any] = {
            "plaintext": base64.b64encode(plaintext).decode("ascii"),
            "algorithm": algorithm,
        }
        if encryption_context:
            body["encryption_context"] = encryption_context

        resp = self._transport.request("POST", "/api/v2/encryption/encrypt", json=body)
        data = resp.data or {}
        return EncryptResult(
            ciphertext=data["ciphertext"],
            encryption_metadata=data["encryption_metadata"],
            signature=data["signature"],
            envelope=data["envelope"],
            request_id=resp.meta.get("request_id"),
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
            verify_signature: Verify ML-DSA-65 signature before decryption
                (strongly recommended, default ``True``).

        Returns:
            DecryptResult with base64-encoded plaintext.
        """
        body: dict[str, Any] = {
            "envelope": envelope,
            "verify_signature": verify_signature,
        }
        resp = self._transport.request("POST", "/api/v2/encryption/decrypt", json=body)
        data = resp.data or {}
        return DecryptResult(
            plaintext=data["plaintext"],
            signature_valid=data["signature_valid"],
            encryption_metadata=data["encryption_metadata"],
            request_id=resp.meta.get("request_id"),
        )

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
            SignResult with PQC signature, HMAC signature, and public key.
        """
        body: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
            "algorithm": algorithm,
        }
        resp = self._transport.request("POST", "/api/v2/encryption/sign", json=body)
        resp_data = resp.data or {}
        return SignResult(
            signature=resp_data["signature"],
            hmac_signature=resp_data["hmac_signature"],
            public_key=resp_data["public_key"],
            algorithm=resp_data["algorithm"],
            request_id=resp.meta.get("request_id"),
        )

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
        body: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
            "signature": signature,
            "hmac_signature": hmac_signature,
            "public_key": public_key,
        }
        if hmac_secret is not None:
            body["hmac_secret"] = hmac_secret

        resp = self._transport.request("POST", "/api/v2/encryption/verify", json=body)
        resp_data = resp.data or {}
        return VerifyResult(
            valid=resp_data["valid"],
            pqc_valid=resp_data["pqc_valid"],
            hmac_valid=resp_data["hmac_valid"],
            algorithm=resp_data["algorithm"],
            verification_metadata=resp_data.get("verification_metadata", {}),
            request_id=resp.meta.get("request_id"),
        )


class AsyncEncryption:
    """Asynchronous quantum-safe encryption operations.

    Same API surface as ``Encryption`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def encrypt(
        self,
        plaintext: bytes,
        *,
        algorithm: str = "ML-KEM-768",
        encryption_context: dict[str, Any] | None = None,
    ) -> EncryptResult:
        """Encrypt data. See ``Encryption.encrypt`` for details."""
        body: dict[str, Any] = {
            "plaintext": base64.b64encode(plaintext).decode("ascii"),
            "algorithm": algorithm,
        }
        if encryption_context:
            body["encryption_context"] = encryption_context

        resp = await self._transport.request("POST", "/api/v2/encryption/encrypt", json=body)
        data = resp.data or {}
        return EncryptResult(
            ciphertext=data["ciphertext"],
            encryption_metadata=data["encryption_metadata"],
            signature=data["signature"],
            envelope=data["envelope"],
            request_id=resp.meta.get("request_id"),
        )

    async def decrypt(
        self,
        envelope: dict[str, Any],
        *,
        verify_signature: bool = True,
    ) -> DecryptResult:
        """Decrypt data. See ``Encryption.decrypt`` for details."""
        body: dict[str, Any] = {
            "envelope": envelope,
            "verify_signature": verify_signature,
        }
        resp = await self._transport.request("POST", "/api/v2/encryption/decrypt", json=body)
        data = resp.data or {}
        return DecryptResult(
            plaintext=data["plaintext"],
            signature_valid=data["signature_valid"],
            encryption_metadata=data["encryption_metadata"],
            request_id=resp.meta.get("request_id"),
        )

    async def sign(
        self,
        data: bytes,
        *,
        algorithm: str = "ML-DSA-65",
    ) -> SignResult:
        """Sign data. See ``Encryption.sign`` for details."""
        body: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
            "algorithm": algorithm,
        }
        resp = await self._transport.request("POST", "/api/v2/encryption/sign", json=body)
        resp_data = resp.data or {}
        return SignResult(
            signature=resp_data["signature"],
            hmac_signature=resp_data["hmac_signature"],
            public_key=resp_data["public_key"],
            algorithm=resp_data["algorithm"],
            request_id=resp.meta.get("request_id"),
        )

    async def verify(
        self,
        data: bytes,
        signature: str,
        hmac_signature: str,
        public_key: str,
        *,
        hmac_secret: str | None = None,
    ) -> VerifyResult:
        """Verify a signature. See ``Encryption.verify`` for details."""
        body: dict[str, Any] = {
            "data": base64.b64encode(data).decode("ascii"),
            "signature": signature,
            "hmac_signature": hmac_signature,
            "public_key": public_key,
        }
        if hmac_secret is not None:
            body["hmac_secret"] = hmac_secret

        resp = await self._transport.request("POST", "/api/v2/encryption/verify", json=body)
        resp_data = resp.data or {}
        return VerifyResult(
            valid=resp_data["valid"],
            pqc_valid=resp_data["pqc_valid"],
            hmac_valid=resp_data["hmac_valid"],
            algorithm=resp_data["algorithm"],
            verification_metadata=resp_data.get("verification_metadata", {}),
            request_id=resp.meta.get("request_id"),
        )
