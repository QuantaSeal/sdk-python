"""Tests for QuantaSeal client initialization and configuration."""

from __future__ import annotations

import os

import pytest

from quantaseal import QuantaSeal, AsyncQuantaSeal


class TestClientInit:
    """Test client initialization paths."""

    def test_init_with_explicit_key(self) -> None:
        client = QuantaSeal(api_key="qsk_test_key", base_url="http://localhost:8000")
        assert repr(client) == "QuantaSeal(base_url='http://localhost:8000')"
        client.close()

    def test_init_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("QUANTASHIELD_API_KEY", "qsk_test_env_key")
        monkeypatch.setenv("QUANTASHIELD_BASE_URL", "http://env-api:8000")
        client = QuantaSeal()
        assert repr(client) == "QuantaSeal(base_url='http://env-api:8000')"
        client.close()

    def test_init_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANTASHIELD_API_KEY", raising=False)
        monkeypatch.delenv("QUANTASEAL_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            QuantaSeal()

    def test_default_base_url(self) -> None:
        client = QuantaSeal(api_key="qsk_test_key")
        assert "api.quantaseal.io" in repr(client)
        client.close()

    def test_context_manager(self) -> None:
        with QuantaSeal(api_key="qsk_test_key", base_url="http://localhost") as qs:
            assert qs.vault is not None
            assert qs.encryption is not None


class TestAsyncClientInit:
    """Test async client initialization."""

    def test_init_with_explicit_key(self) -> None:
        client = AsyncQuantaSeal(api_key="qsk_test_key", base_url="http://localhost:8000")
        assert repr(client) == "AsyncQuantaSeal(base_url='http://localhost:8000')"

    def test_init_no_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("QUANTASHIELD_API_KEY", raising=False)
        monkeypatch.delenv("QUANTASEAL_API_KEY", raising=False)
        with pytest.raises(ValueError, match="api_key must be provided"):
            AsyncQuantaSeal()


class TestEnvironmentNames:
    """QUANTASEAL_* is the documented name; the product's former QUANTASHIELD_* names keep working as a fallback."""

    @staticmethod
    def _clear(monkeypatch: pytest.MonkeyPatch) -> None:
        for name in (
            "QUANTASEAL_API_KEY",
            "QUANTASEAL_BASE_URL",
            "QUANTASHIELD_API_KEY",
            "QUANTASHIELD_BASE_URL",
        ):
            monkeypatch.delenv(name, raising=False)

    def test_new_names_are_read(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._clear(monkeypatch)
        monkeypatch.setenv("QUANTASEAL_API_KEY", "qsk_test_new")
        monkeypatch.setenv("QUANTASEAL_BASE_URL", "http://new-api:8000")
        client = QuantaSeal()
        assert repr(client) == "QuantaSeal(base_url='http://new-api:8000')"
        client.close()

    def test_new_names_win_over_the_old_ones(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._clear(monkeypatch)
        monkeypatch.setenv("QUANTASEAL_API_KEY", "qsk_test_new")
        monkeypatch.setenv("QUANTASHIELD_API_KEY", "qsk_test_old")
        monkeypatch.setenv("QUANTASEAL_BASE_URL", "http://new-api:8000")
        monkeypatch.setenv("QUANTASHIELD_BASE_URL", "http://old-api:8000")
        client = QuantaSeal()
        assert repr(client) == "QuantaSeal(base_url='http://new-api:8000')"
        client.close()

    def test_old_names_still_work(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._clear(monkeypatch)
        monkeypatch.setenv("QUANTASHIELD_API_KEY", "qsk_test_old")
        monkeypatch.setenv("QUANTASHIELD_BASE_URL", "http://old-api:8000")
        client = QuantaSeal()
        assert repr(client) == "QuantaSeal(base_url='http://old-api:8000')"
        client.close()

    def test_explicit_arguments_beat_both(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._clear(monkeypatch)
        monkeypatch.setenv("QUANTASEAL_API_KEY", "qsk_test_new")
        monkeypatch.setenv("QUANTASEAL_BASE_URL", "http://new-api:8000")
        client = QuantaSeal(api_key="qsk_test_arg", base_url="http://arg-api:8000")
        assert repr(client) == "QuantaSeal(base_url='http://arg-api:8000')"
        client.close()
