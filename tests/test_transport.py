"""Tests for HTTP transport layer - retries, error handling, timeouts."""

from __future__ import annotations

import httpx
import pytest
import respx

from quantaseal import QuantaSeal
from quantaseal.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError,
)

from .conftest import API_KEY, BASE_URL, MOCK_ENCRYPT_RESPONSE


class TestRetries:
    """Test retry behaviour for transient failures."""

    def test_retries_on_500(self) -> None:
        """SDK retries on 500 and succeeds on second attempt."""
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt")
            route.side_effect = [
                httpx.Response(500, json={"error": {"message": "Internal Server Error"}}),
                httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE),
            ]

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=2)
            result = qs.encrypt(b"test")
            qs.close()

        assert result.ciphertext == "dGVzdC1jaXBoZXJ0ZXh0"

    def test_retries_on_429(self) -> None:
        """SDK retries on rate limit."""
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt")
            route.side_effect = [
                httpx.Response(
                    429,
                    json={"error": {"message": "Rate limited"}},
                    headers={"Retry-After": "0"},
                ),
                httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE),
            ]

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=2)
            result = qs.encrypt(b"test")
            qs.close()

        assert result.ciphertext == "dGVzdC1jaXBoZXJ0ZXh0"

    def test_max_retries_exceeded(self) -> None:
        """Raises ServerError after max retries exhausted."""
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    500, json={"error": {"message": "Server Error"}}
                )
            )

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=1)
            with pytest.raises(ServerError, match="Server Error"):
                qs.encrypt(b"test")
            qs.close()


class TestErrorMapping:
    """Test HTTP status to exception mapping."""

    def test_401_raises_auth_error(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    401, json={"error": {"message": "Unauthorized"}}
                )
            )

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=0)
            with pytest.raises(AuthenticationError):
                qs.encrypt(b"test")
            qs.close()

    def test_403_raises_auth_error(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    403, json={"error": {"message": "Forbidden"}}
                )
            )

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=0)
            with pytest.raises(AuthenticationError):
                qs.encrypt(b"test")
            qs.close()

    def test_429_includes_retry_after(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    429,
                    json={"error": {"message": "Rate limited"}},
                    headers={"Retry-After": "30"},
                )
            )

            qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=0)
            with pytest.raises(RateLimitError) as exc_info:
                qs.encrypt(b"test")
            assert exc_info.value.retry_after == 30.0
            qs.close()


class TestExceptionAttributes:
    """Test exception attributes are populated."""

    def test_error_repr(self) -> None:
        from quantaseal.exceptions import QuantaSealError

        err = QuantaSealError(
            "test error",
            status_code=500,
            error_code="server_error",
            request_id="req_123",
        )
        repr_str = repr(err)
        assert "test error" in repr_str
        assert "500" in repr_str
        assert "server_error" in repr_str
        assert "req_123" in repr_str
