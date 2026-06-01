"""Auth resource for authentication and MFA operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantaseal._transport import AsyncTransport, SyncTransport


class Auth:
    """Synchronous authentication operations - login, register, token refresh, MFA.

    Usage::

        qs = QuantaSeal(api_key="qs_test_...")

        # Login and receive tokens
        tokens = qs.auth.login("user@example.com", "password123")

        # Refresh an access token
        refreshed = qs.auth.refresh(tokens["refresh_token"])

        # Setup MFA
        mfa_info = qs.auth.setup_mfa()
        print(mfa_info["qr_code_url"])

        # Verify MFA
        qs.auth.verify_mfa("123456")
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate with email and password.

        Args:
            email: User email address.
            password: User password.

        Returns:
            Dict containing ``access_token``, ``refresh_token``, and ``expires_in``.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/auth/login",
            json={"email": email, "password": password},
        )
        return resp.data or {}

    def register(self, email: str, password: str, org_name: str) -> dict[str, Any]:
        """Register a new user and organisation.

        Args:
            email: User email address.
            password: Desired password (min 12 characters recommended).
            org_name: Organisation / tenant display name.

        Returns:
            Dict containing the created ``user_id``, ``org_id``, and initial tokens.

        Raises:
            ValidationError: If the email is already registered or password is too weak.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/auth/register",
            json={"email": email, "password": password, "org_name": org_name},
        )
        return resp.data or {}

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: A valid refresh token obtained from ``login()``.

        Returns:
            Dict containing new ``access_token`` and ``expires_in``.

        Raises:
            AuthenticationError: If the refresh token is expired or invalid.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        return resp.data or {}

    def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token (logout).

        Args:
            refresh_token: The refresh token to invalidate.
        """
        self._transport.request_raw(
            "POST",
            "/api/v2/auth/logout",
            json={"refresh_token": refresh_token},
        )

    def setup_mfa(self) -> dict[str, Any]:
        """Initiate TOTP-based MFA setup for the current user.

        Returns:
            Dict containing ``secret``, ``qr_code_url``, and ``backup_codes``.
        """
        resp = self._transport.request("POST", "/api/v2/auth/mfa/setup")
        return resp.data or {}

    def verify_mfa(self, totp_code: str) -> dict[str, Any]:
        """Verify a TOTP code and activate MFA.

        Args:
            totp_code: 6-digit TOTP code from an authenticator app.

        Returns:
            Dict with ``verified`` bool and any updated token claims.

        Raises:
            ValidationError: If the TOTP code is invalid or expired.
        """
        resp = self._transport.request(
            "POST",
            "/api/v2/auth/mfa/verify",
            json={"totp_code": totp_code},
        )
        return resp.data or {}


class AsyncAuth:
    """Asynchronous authentication operations.

    Same API surface as ``Auth`` but all methods are ``async``.
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate with email and password. See ``Auth.login`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/auth/login",
            json={"email": email, "password": password},
        )
        return resp.data or {}

    async def register(self, email: str, password: str, org_name: str) -> dict[str, Any]:
        """Register a new user and organisation. See ``Auth.register`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/auth/register",
            json={"email": email, "password": password, "org_name": org_name},
        )
        return resp.data or {}

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an access token. See ``Auth.refresh`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        return resp.data or {}

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token. See ``Auth.logout`` for details."""
        await self._transport.request_raw(
            "POST",
            "/api/v2/auth/logout",
            json={"refresh_token": refresh_token},
        )

    async def setup_mfa(self) -> dict[str, Any]:
        """Initiate MFA setup. See ``Auth.setup_mfa`` for details."""
        resp = await self._transport.request("POST", "/api/v2/auth/mfa/setup")
        return resp.data or {}

    async def verify_mfa(self, totp_code: str) -> dict[str, Any]:
        """Verify a TOTP code. See ``Auth.verify_mfa`` for details."""
        resp = await self._transport.request(
            "POST",
            "/api/v2/auth/mfa/verify",
            json={"totp_code": totp_code},
        )
        return resp.data or {}
