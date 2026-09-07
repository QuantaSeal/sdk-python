"""Tests for async QuantaSeal client operations."""

from __future__ import annotations

import httpx
import pytest
import respx

from quantaseal import AsyncQuantaSeal

from .conftest import (
    API_KEY,
    BASE_URL,
    MOCK_ENCRYPT_RESPONSE,
    MOCK_SIGN_RESPONSE,
    MOCK_VAULT_LIST_RESPONSE,
    MOCK_VAULT_SEAL_RESPONSE,
    MOCK_VAULT_UNSEAL_RESPONSE,
)


class TestAsyncEncrypt:
    """Test async encryption operations."""

    @pytest.mark.asyncio
    async def test_encrypt_success(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                result = await qs.encrypt(b"hello world")

        assert result.ciphertext == "dGVzdC1jaXBoZXJ0ZXh0"
        assert result.algorithm == "ML-KEM-768"

    @pytest.mark.asyncio
    async def test_sign_success(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/sign").mock(
                return_value=httpx.Response(200, json=MOCK_SIGN_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                result = await qs.sign(b"message")

        assert result.algorithm == "ML-DSA-65"
        assert result.signature == "cHFjLXNpZw=="


class TestAsyncVault:
    """Test async vault operations."""

    @pytest.mark.asyncio
    async def test_seal_success(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/seal").mock(
                return_value=httpx.Response(201, json=MOCK_VAULT_SEAL_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                entry_id = await qs.vault.seal(
                    name="test-cred",
                    credential_type="api_key",
                    plaintext={"key": "value"},
                )

        assert entry_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    @pytest.mark.asyncio
    async def test_unseal_success(self) -> None:
        entry_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/unseal/{entry_id}").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_UNSEAL_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                result = await qs.vault.unseal(entry_id)

        assert result.plaintext["access_key"] == "AKIAIOSFODNN7EXAMPLE"

    @pytest.mark.asyncio
    async def test_list_entries(self) -> None:
        with respx.mock:
            respx.get(f"{BASE_URL}/api/v2/vault/entries").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_LIST_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                entries = await qs.vault.list()

        assert len(entries) == 2
        assert entries[0].name == "aws-prod-keys"

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        entry_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        with respx.mock:
            respx.delete(f"{BASE_URL}/api/v2/vault/entries/{entry_id}").mock(
                return_value=httpx.Response(204)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                await qs.vault.delete(entry_id)


class TestAsyncContextManager:
    """Test async context manager."""

    @pytest.mark.asyncio
    async def test_async_with(self) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
                return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
            )
            async with AsyncQuantaSeal(
                api_key=API_KEY, base_url=BASE_URL, max_retries=0
            ) as qs:
                result = await qs.encrypt(b"test")

        assert result.ciphertext is not None
