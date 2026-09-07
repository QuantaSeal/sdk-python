"""Tests for QuantaSeal client initialization and configuration."""

from __future__ import annotations

import os

import pytest

from quantaseal import QuantaSeal, AsyncQuantaSeal


class TestClientInit:
    """Test client initialization paths."""

    def test_init_with_explicit_key(self) -> None:
        client = QuantaSeal(api_key="qs_test_key", base_url="http://localhost:8000")
        assert repr(client) == "QuantaSeal(base_url='http://localhost:8000')"
        client.close()

    def test_init_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("QUANTASHIELD_API_KEY", "qs_test_env_key")
        monkeypatch.setenv("QUANTASHIELD_BASE_URL", "http://env-api:8000")
        client = QuantaSeal()
        assert repr(client) == "QuantaSeal(base_url='http://env-api:8000')"
        client.close()

    def test_init_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANTASHIELD_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            QuantaSeal()

    def test_default_base_url(self) -> None:
        client = QuantaSeal(api_key="qs_test_key")
        assert "api.quantaseal.io" in repr(client)
        client.close()

    def test_context_manager(self) -> None:
        with QuantaSeal(api_key="qs_test_key", base_url="http://localhost") as qs:
            assert qs.vault is not None
            assert qs.encryption is not None


class TestAsyncClientInit:
    """Test async client initialization."""

    def test_init_with_explicit_key(self) -> None:
        client = AsyncQuantaSeal(api_key="qs_test_key", base_url="http://localhost:8000")
        assert repr(client) == "AsyncQuantaSeal(base_url='http://localhost:8000')"

    def test_init_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANTASHIELD_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            AsyncQuantaSeal()
