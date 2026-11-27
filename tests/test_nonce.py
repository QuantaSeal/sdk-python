"""Anti-replay: every mutating call carries a unique X-Nonce; reads do not; a retry never reuses one."""

from __future__ import annotations

import re

import httpx
import respx

from quantaseal import QuantaSeal

from .conftest import API_KEY, BASE_URL, MOCK_ENCRYPT_RESPONSE

# the server accepts 16-64 characters of letters, digits and hyphens
NONCE_RULE = re.compile(r"^[A-Za-z0-9-]{16,64}$")


def test_a_mutating_call_sends_a_valid_nonce() -> None:
    with respx.mock:
        route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
            return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
        )
        qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL)
        qs.encrypt(b"x")
        qs.close()
    nonce = route.calls.last.request.headers.get("X-Nonce")
    assert nonce is not None and NONCE_RULE.match(nonce)


def test_each_call_gets_its_own_nonce() -> None:
    with respx.mock:
        route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt").mock(
            return_value=httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE)
        )
        qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL)
        qs.encrypt(b"a")
        qs.encrypt(b"b")
        qs.close()
    nonces = [call.request.headers["X-Nonce"] for call in route.calls]
    assert len(set(nonces)) == 2


def test_a_retry_uses_a_new_nonce() -> None:
    """A reused nonce is rejected as a replay (409), so the retry after a 500 must not send the first one again."""
    with respx.mock:
        route = respx.post(f"{BASE_URL}/api/v2/encryption/encrypt")
        route.side_effect = [
            httpx.Response(500, json={"error": {"message": "boom"}}),
            httpx.Response(200, json=MOCK_ENCRYPT_RESPONSE),
        ]
        qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL, max_retries=2)
        qs.encrypt(b"x")
        qs.close()
    first, second = (call.request.headers["X-Nonce"] for call in route.calls)
    assert first != second and NONCE_RULE.match(second)


def test_a_read_sends_no_nonce() -> None:
    with respx.mock:
        route = respx.get(f"{BASE_URL}/api/v2/vault/entries").mock(
            return_value=httpx.Response(200, json={"success": True, "data": []})
        )
        qs = QuantaSeal(api_key=API_KEY, base_url=BASE_URL)
        try:
            qs.vault.list()
        except Exception:  # noqa: BLE001 - only the request headers matter here
            pass
        qs.close()
    assert route.called
    assert "X-Nonce" not in route.calls.last.request.headers
