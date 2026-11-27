"""Tests for vault operations (seal, unseal, rotate, list, delete)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from quantaseal import QuantaSeal
from quantaseal.exceptions import NotFoundError, VaultError

from .conftest import (
    API_KEY,
    BASE_URL,
    MOCK_VAULT_LIST_RESPONSE,
    MOCK_VAULT_ROTATE_RESPONSE,
    MOCK_VAULT_SEAL_RESPONSE,
    MOCK_VAULT_UNSEAL_RESPONSE,
)


@pytest.fixture
def qs() -> QuantaSeal:
    client = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=0)
    yield client
    client.close()


class TestVaultSeal:
    """Test vault seal operations."""

    def test_seal_success(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/seal").mock(
                return_value=httpx.Response(201, json=MOCK_VAULT_SEAL_RESPONSE)
            )
            entry_id = qs.vault.seal(
                name="aws-prod-keys",
                credential_type="api_key",
                plaintext={"access_key": "AKIA...", "secret_key": "wJal..."},
            )

        assert entry_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    def test_seal_with_ttl_and_metadata(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/vault/seal").mock(
                return_value=httpx.Response(201, json=MOCK_VAULT_SEAL_RESPONSE)
            )
            qs.vault.seal(
                name="temp-creds",
                credential_type="password",
                plaintext={"password": "s3cret"},
                ttl_days=30,
                metadata={"environment": "staging"},
            )
            body = json.loads(route.calls.last.request.content)

        assert body["ttl_days"] == 30
        assert body["metadata"] == {"environment": "staging"}

    def test_seal_sends_correct_body(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.post(f"{BASE_URL}/api/v2/vault/seal").mock(
                return_value=httpx.Response(201, json=MOCK_VAULT_SEAL_RESPONSE)
            )
            qs.vault.seal(
                name="test-cred",
                credential_type="certificate",
                plaintext={"cert": "-----BEGIN CERTIFICATE-----"},
            )
            body = json.loads(route.calls.last.request.content)

        assert body["name"] == "test-cred"
        assert body["credential_type"] == "certificate"
        assert "ttl_days" not in body


class TestVaultUnseal:
    """Test vault unseal operations."""

    def test_unseal_success(self, qs: QuantaSeal) -> None:
        entry_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/unseal/{entry_id}").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_UNSEAL_RESPONSE)
            )
            result = qs.vault.unseal(entry_id)

        assert result.plaintext["access_key"] == "AKIAIOSFODNN7EXAMPLE"
        assert result.last_accessed_at == "2026-03-02T12:00:05Z"
        assert result.request_id == "req_unseal12"

    def test_unseal_not_found(self, qs: QuantaSeal) -> None:
        entry_id = "nonexistent-uuid"
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/unseal/{entry_id}").mock(
                return_value=httpx.Response(
                    404,
                    json={
                        "success": False,
                        "error": {"message": "Vault entry not found"},
                        "meta": {},
                    },
                )
            )
            with pytest.raises(NotFoundError, match="not found"):
                qs.vault.unseal(entry_id)

    def test_unseal_expired(self, qs: QuantaSeal) -> None:
        entry_id = "expired-uuid"
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/unseal/{entry_id}").mock(
                return_value=httpx.Response(
                    410,
                    json={
                        "success": False,
                        "error": {"message": "Vault entry has expired"},
                        "meta": {},
                    },
                )
            )
            with pytest.raises(VaultError, match="expired"):
                qs.vault.unseal(entry_id)


class TestVaultList:
    """Test vault list operations."""

    def test_list_entries(self, qs: QuantaSeal) -> None:
        with respx.mock:
            respx.get(f"{BASE_URL}/api/v2/vault/entries").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_LIST_RESPONSE)
            )
            entries = qs.vault.list()

        assert len(entries) == 2
        assert entries[0].name == "aws-prod-keys"
        assert entries[0].credential_type == "api_key"
        assert entries[0].is_active is True
        assert entries[1].name == "stripe-api-key"
        assert entries[1].last_accessed_at is None

    def test_list_with_inactive(self, qs: QuantaSeal) -> None:
        with respx.mock:
            route = respx.get(f"{BASE_URL}/api/v2/vault/entries").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_LIST_RESPONSE)
            )
            qs.vault.list(include_inactive=True)
            url = str(route.calls.last.request.url)

        assert "include_inactive=true" in url


class TestVaultRotate:
    """Test vault rotate operations."""

    def test_rotate_success(self, qs: QuantaSeal) -> None:
        entry_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        with respx.mock:
            respx.post(f"{BASE_URL}/api/v2/vault/rotate/{entry_id}").mock(
                return_value=httpx.Response(200, json=MOCK_VAULT_ROTATE_RESPONSE)
            )
            result = qs.vault.rotate(entry_id)

        assert result.new_entry_id == "new-uuid-1234-5678-abcd-ef1234567890"
        assert result.old_entry_id == entry_id


class TestVaultDelete:
    """Test vault delete operations."""

    def test_delete_success(self, qs: QuantaSeal) -> None:
        entry_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        with respx.mock:
            respx.delete(f"{BASE_URL}/api/v2/vault/entries/{entry_id}").mock(
                return_value=httpx.Response(204)
            )
            qs.vault.delete(entry_id)

    def test_delete_not_found(self, qs: QuantaSeal) -> None:
        entry_id = "nonexistent-uuid"
        with respx.mock:
            respx.delete(f"{BASE_URL}/api/v2/vault/entries/{entry_id}").mock(
                return_value=httpx.Response(
                    404,
                    json={
                        "success": False,
                        "error": {"message": "Vault entry not found"},
                        "meta": {},
                    },
                )
            )
            with pytest.raises(NotFoundError, match="not found"):
                qs.vault.delete(entry_id)
