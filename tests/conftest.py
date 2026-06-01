"""Shared test fixtures for QuantaSeal SDK tests."""

from __future__ import annotations

import pytest

from quantaseal import QuantaSeal

# ─────────────────────────────────────────────────────────────────────────────
# Mock API response payloads
# ─────────────────────────────────────────────────────────────────────────────

MOCK_ENCRYPT_RESPONSE = {
    "success": True,
    "data": {
        "ciphertext": "dGVzdC1jaXBoZXJ0ZXh0",
        "encryption_metadata": {
            "algorithm": "ML-KEM-768",
            "nonce": "dGVzdC1ub25jZQ==",
            "tenant_id": "t-001",
            "key_id": "k-001",
        },
        "signature": "c2lnbmF0dXJl",
        "envelope": {
            "encrypted_payload": {
                "algorithm": "ML-KEM-768",
                "ciphertext_data": "dGVzdC1jaXBoZXJ0ZXh0",
                "nonce": "dGVzdC1ub25jZQ==",
                "tenant_id": "t-001",
            },
            "signed_payload": {
                "pqc_signature": "c2lnbmF0dXJl",
                "algorithm": "ML-DSA-65",
            },
        },
    },
    "error": None,
    "meta": {
        "request_id": "req_abc12345",
        "timestamp": "2026-03-02T12:00:00Z",
        "version": "2.0",
    },
}

MOCK_DECRYPT_RESPONSE = {
    "success": True,
    "data": {
        "plaintext": "aGVsbG8gd29ybGQ=",
        "signature_valid": True,
        "encryption_metadata": {
            "algorithm": "ML-KEM-768",
            "key_id": "k-001",
        },
    },
    "error": None,
    "meta": {"request_id": "req_dec12345", "timestamp": "2026-03-02T12:00:01Z"},
}

MOCK_SIGN_RESPONSE = {
    "success": True,
    "data": {
        "signature": "cHFjLXNpZw==",
        "hmac_signature": "aG1hYy1zaWc=",
        "public_key": "cHVibGljLWtleQ==",
        "algorithm": "ML-DSA-65",
    },
    "error": None,
    "meta": {"request_id": "req_sig12345", "timestamp": "2026-03-02T12:00:02Z"},
}

MOCK_VERIFY_RESPONSE = {
    "success": True,
    "data": {
        "valid": True,
        "pqc_valid": True,
        "hmac_valid": True,
        "algorithm": "ML-DSA-65",
        "verification_metadata": {},
    },
    "error": None,
    "meta": {"request_id": "req_ver12345", "timestamp": "2026-03-02T12:00:03Z"},
}

MOCK_VAULT_SEAL_RESPONSE = {
    "success": True,
    "data": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "error": None,
    "meta": {"request_id": "req_seal1234", "timestamp": "2026-03-02T12:00:04Z"},
}

MOCK_VAULT_UNSEAL_RESPONSE = {
    "success": True,
    "data": {
        "plaintext": {"access_key": "AKIAIOSFODNN7EXAMPLE", "secret_key": "wJalr..."},
        "last_accessed_at": "2026-03-02T12:00:05Z",
    },
    "error": None,
    "meta": {"request_id": "req_unseal12", "timestamp": "2026-03-02T12:00:05Z"},
}

MOCK_VAULT_LIST_RESPONSE = {
    "success": True,
    "data": [
        {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "name": "aws-prod-keys",
            "credential_type": "api_key",
            "algorithm": "ML-KEM-768",
            "is_active": True,
            "created_at": "2026-03-01T10:00:00Z",
            "last_accessed_at": "2026-03-02T12:00:00Z",
            "ttl_expires_at": "2026-06-01T10:00:00Z",
        },
        {
            "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
            "name": "stripe-api-key",
            "credential_type": "api_key",
            "algorithm": "ML-KEM-768",
            "is_active": True,
            "created_at": "2026-02-15T08:00:00Z",
            "last_accessed_at": None,
            "ttl_expires_at": None,
        },
    ],
    "error": None,
    "meta": {"request_id": "req_list1234", "timestamp": "2026-03-02T12:00:06Z"},
}

MOCK_VAULT_ROTATE_RESPONSE = {
    "success": True,
    "data": {
        "new_entry_id": "new-uuid-1234-5678-abcd-ef1234567890",
        "old_entry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    },
    "error": None,
    "meta": {"request_id": "req_rot12345", "timestamp": "2026-03-02T12:00:07Z"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.test.quantaseal.io"
API_KEY = "qs_test_fixture_key_abc123"


@pytest.fixture
def base_url() -> str:
    return BASE_URL


@pytest.fixture
def api_key() -> str:
    return API_KEY
