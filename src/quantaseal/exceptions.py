"""Exception hierarchy for the QuantaSeal Python SDK."""

from __future__ import annotations

from typing import Any


class QuantaSealError(Exception):
    """Base exception for all QuantaSeal SDK errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code from the API (if applicable).
        error_code: Machine-readable error code from the API.
        details: Additional error context from the API response.
        request_id: Request ID for support/debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.request_id = request_id

    def __repr__(self) -> str:
        parts = [f"message={self.message!r}"]
        if self.status_code:
            parts.append(f"status_code={self.status_code}")
        if self.error_code:
            parts.append(f"error_code={self.error_code!r}")
        if self.request_id:
            parts.append(f"request_id={self.request_id!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"


class AuthenticationError(QuantaSealError):
    """Raised when authentication fails (401/403).

    Common causes:
    - Invalid or expired API key
    - Missing Authorization header
    - Insufficient permissions for the requested operation
    """


class ValidationError(QuantaSealError):
    """Raised when request validation fails (400/422).

    Common causes:
    - Invalid base64 encoding for plaintext/ciphertext
    - Missing required fields
    - Invalid credential type for vault operations
    """


class RateLimitError(QuantaSealError):
    """Raised when rate limits are exceeded (429).

    Attributes:
        retry_after: Seconds to wait before retrying.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class NotFoundError(QuantaSealError):
    """Raised when a requested resource is not found (404).

    Common causes:
    - Invalid vault entry ID
    - Deleted or expired vault entry
    """


class ServerError(QuantaSealError):
    """Raised when the QuantaSeal API returns a server error (5xx).

    These errors are typically transient and can be retried.
    """


class VaultError(QuantaSealError):
    """Raised for vault-specific errors.

    Common causes:
    - Vault entry expired (410 Gone)
    - Decryption failure (corrupted or tampered entry)
    - Credential rotation failure
    """


class ConnectionError(QuantaSealError):
    """Raised when the SDK cannot connect to the QuantaSeal API.

    Common causes:
    - Network connectivity issues
    - DNS resolution failure
    - API server unreachable
    - TLS handshake failure
    """


class TimeoutError(QuantaSealError):
    """Raised when an API request times out."""
