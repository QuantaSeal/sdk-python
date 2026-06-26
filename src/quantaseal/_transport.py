"""HTTP transport layer for the QuantaSeal SDK."""

from __future__ import annotations

import time
from typing import Any

import httpx

from quantaseal._version import __version__
from quantaseal.exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    QuantaSealError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from quantaseal.models import APIResponse

_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 3
_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
_RETRY_BACKOFF_FACTOR = 0.5


def _build_headers(api_key: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Build standard request headers."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"quantaseal-python/{__version__}",
        "X-SDK-Version": __version__,
        "X-SDK-Language": "python",
    }
    if extra:
        headers.update(extra)
    return headers


def _raise_for_status(response: httpx.Response) -> None:
    """Parse API error response and raise appropriate exception."""
    status = response.status_code

    try:
        body = response.json()
    except Exception:
        body = {"error": {"message": response.text or "Unknown error"}}

    error_data = body.get("error") or {}
    meta = body.get("meta") or {}
    message = (
        error_data.get("message")
        or error_data.get("detail")
        or body.get("detail")
        or f"HTTP {status}"
    )
    error_code = error_data.get("code")
    request_id = meta.get("request_id")
    details = error_data.get("details")

    kwargs: dict[str, Any] = {
        "status_code": status,
        "error_code": error_code,
        "details": details,
        "request_id": request_id,
    }

    if status in (401, 403):
        raise AuthenticationError(message, **kwargs)
    if status in (400, 422):
        raise ValidationError(message, **kwargs)
    if status == 404:
        raise NotFoundError(message, **kwargs)
    if status == 410:
        from quantaseal.exceptions import VaultError

        raise VaultError(message, **kwargs)
    if status == 429:
        retry_after = response.headers.get("Retry-After")
        raise RateLimitError(
            message,
            retry_after=float(retry_after) if retry_after else None,
            **kwargs,
        )
    if status >= 500:
        raise ServerError(message, **kwargs)

    raise QuantaSealError(message, **kwargs)


class SyncTransport:
    """Synchronous HTTP transport backed by httpx."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key, headers),
            timeout=timeout,
            follow_redirects=True,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> APIResponse:
        """Make an HTTP request with retries."""
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                if response.status_code < 400:
                    return APIResponse.model_validate(response.json())

                if response.status_code in _RETRY_STATUS_CODES and attempt < self._max_retries:
                    _sleep_backoff(attempt, response)
                    continue

                _raise_for_status(response)

            except httpx.ConnectError as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    _sleep_backoff(attempt)
                    continue
                raise ConnectionError(
                    f"Failed to connect to {self._base_url}: {exc}"
                ) from exc

            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    _sleep_backoff(attempt)
                    continue
                raise TimeoutError(
                    f"Request timed out after {self._client.timeout.read}s"
                ) from exc

            except (QuantaSealError, KeyboardInterrupt):
                raise

            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    _sleep_backoff(attempt)
                    continue
                raise QuantaSealError(f"Unexpected error: {exc}") from exc

        raise QuantaSealError(f"Max retries ({self._max_retries}) exceeded") from last_exc

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a raw HTTP request (for endpoints with no response body, e.g., DELETE 204)."""
        response = self._client.request(method, path, json=json, params=params)
        if response.status_code >= 400:
            _raise_for_status(response)
        return response

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()


class AsyncTransport:
    """Asynchronous HTTP transport backed by httpx."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key, headers),
            timeout=timeout,
            follow_redirects=True,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> APIResponse:
        """Make an async HTTP request with retries."""
        import asyncio

        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                )
                if response.status_code < 400:
                    return APIResponse.model_validate(response.json())

                if response.status_code in _RETRY_STATUS_CODES and attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt, response))
                    continue

                _raise_for_status(response)

            except httpx.ConnectError as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise ConnectionError(
                    f"Failed to connect to {self._base_url}: {exc}"
                ) from exc

            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise TimeoutError(
                    f"Request timed out after {self._client.timeout.read}s"
                ) from exc

            except (QuantaSealError, KeyboardInterrupt):
                raise

            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise QuantaSealError(f"Unexpected error: {exc}") from exc

        raise QuantaSealError(f"Max retries ({self._max_retries}) exceeded") from last_exc

    async def request_raw(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a raw async HTTP request (for endpoints with no response body)."""
        response = await self._client.request(method, path, json=json, params=params)
        if response.status_code >= 400:
            _raise_for_status(response)
        return response

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()


# ─────────────────────────────────────────────────────────────────────────────
# Retry helpers
# ─────────────────────────────────────────────────────────────────────────────


def _backoff_delay(attempt: int, response: httpx.Response | None = None) -> float:
    """Calculate exponential backoff delay with jitter."""
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
    return _RETRY_BACKOFF_FACTOR * (2**attempt)


def _sleep_backoff(attempt: int, response: httpx.Response | None = None) -> None:
    """Sleep with exponential backoff."""
    time.sleep(_backoff_delay(attempt, response))
