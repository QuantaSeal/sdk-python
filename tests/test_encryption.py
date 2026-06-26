"""Tests for encryption operations (encrypt, decrypt, sign, verify)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from quantaseal import QuantaSeal
from quantaseal.exceptions import AuthenticationError, ValidationError

from .conftest import (
    API_KEY,
    BASE_URL,
    MOCK_DECRYPT_RESPONSE,
    MOCK_ENCRYPT_RESPONSE,
    MOCK_SIGN_RESPONSE,
    MOCK_VERIFY_RESPONSE,
)


@pytest.fixture
def qs() -> QuantaSeal:
    client = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=0)
    yield client
    client.close()


class TestEncrypt:
    """Test encrypt operations."""

    def test_encrypt_success(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
            )
            result = qs.encrypt(b"hello world")

        assert result.ciphertext == "dGVzdC1jaXBoZXJ0ZXh0"
        assert result.algorithm == "ML-KEM-768"
        assert result.key_id == "k-001"
        assert result.signature == "c2lnbmF0dXJl"
        assert result.envelope is not None
        assert result.request_id == "req_abc12345"

    def test_encrypt_with_context(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
            )
            qs.encrypt(
                b"data",
                algorithm="ML-KEM-768",
                encryption_context={"purpose": "test"},
            )
            body = json.loads(route.calls.last.request.content)

        assert body["encryption_context"] == {"purpose": "test"}

    def test_encrypt_auth_error(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    401,
                    json={
                        "success": False,
                        "error": {"message": "Invalid API key", "code": "auth_error"},
                        "meta": {"request_id": "req_err"},
                    },
                )
            )
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                qs.encrypt(b"data")

    def test_encrypt_validation_error(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(
                    422,
                    json={
                        "success": False,
                        "error": {"message": "Invalid base64 encoding"},
                        "meta": {},
                    },
                )
            )
            with pytest.raises(ValidationError, match="Invalid base64"):
                qs.encrypt(b"data")


class TestDecrypt:
    """Test decrypt operations."""

    def test_decrypt_success(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/decrypt").mock(
                return_value=httpx.Response(200, json=MOCK_DECRYPT_RESPONSE)
            )
            result = qs.decrypt(MOCK_ENCRYPT_RESPONSE["data"]["envelope"])

        assert result.plaintext == "aGVsbG8gd29ybGQ="
        assert result.signature_valid is True
        assert result.request_id == "req_dec12345"

    def test_decrypt_without_verify(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/encryption/decrypt").mock(
                return_value=httpx.Response(200, json=MOCK_DECRYPT_RESPONSE)
            )
            qs.decrypt({"envelope": "data"}, verify_signature=False)
            body = json.loads(route.calls.last.request.content)

        assert body["verify_signature"] is False


class TestSign:
    """Test sign operations."""

    def test_sign_success(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/sign").mock(
                return_value=httpx.Response(200, json=MOCK_SIGN_RESPONSE)
            )
            result = qs.sign(b"message to sign")

        assert result.signature == "cHFjLXNpZw=="
        assert result.hmac_signature == "aG1hYy1zaWc="
        assert result.public_key == "cHVibGljLWtleQ=="
        assert result.algorithm == "ML-DSA-65"
        assert result.request_id == "req_sig12345"


class TestVerify:
    """Test verify operations."""

    def test_verify_success(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/verify").mock(
                return_value=httpx.Response(200, json=MOCK_VERIFY_RESPONSE)
            )
            result = qs.verify(
                data=b"original data",
                signature="cHFjLXNpZw==",
                hmac_signature="aG1hYy1zaWc=",
                public_key="cHVibGljLWtleQ==",
            )

        assert result.valid is True
        assert result.pqc_valid is True
        assert result.hmac_valid is True
        assert result.algorithm == "ML-DSA-65"

    def test_verify_with_hmac_secret(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/encryption/verify").mock(
                return_value=httpx.Response(200, json=MOCK_VERIFY_RESPONSE)
            )
            qs.verify(
                data=b"data",
                signature="sig",
                hmac_signature="hmac",
                public_key="pk",
                hmac_secret="custom-secret",
            )
            body = json.loads(route.calls.last.request.content)

        assert body["hmac_secret"] == "custom-secret"
