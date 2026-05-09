from __future__ import annotations

import pytest

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3.client import Client
from maicoin.v3.client import RetryPolicy
from maicoin.v3.errors import MaxAPIError
from maicoin.v3.errors import MaxHTTPError
from maicoin.v3.models import InterestRate
from maicoin.v3.models import Market
from maicoin.v3.models import Timestamp
from tests.v3.helpers import FakeResponse
from tests.v3.helpers import FakeSession
from tests.v3.helpers import last_kwargs
from tests.v3.helpers import request_headers

pytestmark = pytest.mark.anyio


async def test_get_request_sends_params_as_query_params() -> None:
    session = FakeSession(FakeResponse([{"id": "btctwd"}]))
    client = Client(base_url="https://example.test", session=session)

    assert await client.request("GET", "/api/v3/markets", params={"foo": "bar"}) == [{"id": "btctwd"}]

    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/markets"
    assert last_kwargs(session)["params"] == {"foo": "bar"}
    assert "json" not in last_kwargs(session)


async def test_post_request_sends_params_as_json_body() -> None:
    session = FakeSession(FakeResponse({"id": 1}))
    client = Client(base_url="https://example.test", session=session)

    assert await client.request("POST", "api/v3/order", params={"market": "btctwd"}) == {"id": 1}

    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(session)["json"] == {"market": "btctwd"}
    assert "params" not in last_kwargs(session)


async def test_delete_request_sends_params_as_json_body() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(base_url="https://example.test", session=session)

    assert await client.request("DELETE", "/api/v3/order", params={"id": 1}) == {"ok": True}

    assert session.calls[-1]["method"] == "DELETE"
    assert last_kwargs(session)["json"] == {"id": 1}
    assert "params" not in last_kwargs(session)


async def test_authenticated_request_adds_max_headers() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )

    await client.request("GET", "/api/v3/wallet/spot/accounts", params={"currency": "btc"}, auth=True)

    headers = request_headers(session)
    assert headers["X-MAX-ACCESSKEY"] == "key"
    assert headers["X-MAX-PAYLOAD"] == (
        "eyJub25jZSI6MTIzNDU2LCJjdXJyZW5jeSI6ImJ0YyIsInBhdGgiOiIvYXBpL3YzL3dhbGxldC9zcG90L2FjY291bnRzIn0="
    )
    assert headers["X-MAX-SIGNATURE"] == "4347a83e4172fdf36e00c954deacfe143e77a360daef361106ff1ea852cceabe"
    assert headers["Content-Type"] == "application/json"
    assert last_kwargs(session)["params"] == {"nonce": 123456, "currency": "btc"}


async def test_http_error_response_raises() -> None:
    client = Client(
        base_url="https://example.test",
        session=FakeSession(FakeResponse({"error": "invalid nonce"}, status_code=401)),
    )

    with pytest.raises(MaxHTTPError, match="invalid nonce"):
        await client.request("GET", "/api/v3/wallet/spot/accounts")


async def test_api_error_payload_raises() -> None:
    client = Client(base_url="https://example.test", session=FakeSession(FakeResponse({"error": "bad request"})))

    with pytest.raises(MaxAPIError, match="bad request"):
        await client.request("GET", "/api/v3/ticker")


async def test_authenticated_request_requires_credentials() -> None:
    client = Client(base_url="https://example.test", session=FakeSession(FakeResponse({})))

    with pytest.raises(ValueError, match="api_key and api_secret"):
        await client.request("GET", "/api/v3/wallet/spot/accounts", auth=True)


async def test_endpoint_executor_preserves_request_conventions_and_parse_payloads() -> None:
    market_payload = {
        "id": "btctwd",
        "status": "enabled",
        "base_unit": "btc",
        "base_unit_precision": 8,
        "min_base_amount": 0.0001,
        "quote_unit": "twd",
        "quote_unit_precision": 2,
        "min_quote_amount": 100.0,
        "m_wallet_supported": True,
    }
    session = FakeSession(
        [
            FakeResponse({"timestamp": 1678766175}),
            FakeResponse([market_payload]),
            FakeResponse({"btc": {"hourly_interest_rate": "0.0003", "next_hourly_interest_rate": "0.0004"}}),
        ]
    )
    client = Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )
    endpoint = EndpointExecutor(client)

    timestamp = await endpoint.model(EndpointSpec("GET", "/api/v3/timestamp"), Timestamp)
    markets = await endpoint.model_list(EndpointSpec("GET", "/api/v3/markets"), Market)
    rates = await endpoint.model_mapping(
        EndpointSpec("GET", "/api/v3/wallet/m/interest_rates", auth=True),
        InterestRate,
        {"currency": None},
    )

    assert timestamp.timestamp == 1678766175
    assert markets == [Market.model_validate(market_payload)]
    assert rates["btc"].hourly_interest_rate == "0.0003"
    assert [call["url"] for call in session.calls] == [
        "https://example.test/api/v3/timestamp",
        "https://example.test/api/v3/markets",
        "https://example.test/api/v3/wallet/m/interest_rates",
    ]
    assert last_kwargs(session)["params"] == {"nonce": 123456}


async def test_get_request_retries_retry_after_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []

    async def sleep(delay: float) -> None:
        sleeps.append(delay)

    session = FakeSession(
        [
            FakeResponse({"error": "rate limited"}, status_code=429, headers={"Retry-After": "0"}),
            FakeResponse({"ok": True}),
        ]
    )
    client = Client(base_url="https://example.test", session=session, retry_policy=RetryPolicy(jitter=0))
    monkeypatch.setattr(client, "_sleep_before_retry", sleep)

    assert await client.request("GET", "/api/v3/ping") == {"ok": True}
    assert len(session.calls) == 2
    assert sleeps == [0.0]


async def test_post_request_does_not_retry_by_default() -> None:
    session = FakeSession(
        [
            FakeResponse({"error": "gateway"}, status_code=503),
            FakeResponse({"ok": True}),
        ]
    )
    client = Client(base_url="https://example.test", session=session, retry_policy=RetryPolicy(jitter=0))

    with pytest.raises(MaxHTTPError, match="gateway"):
        await client.request("POST", "/api/v3/order", params={"market": "btctwd"})

    assert len(session.calls) == 1


async def test_post_request_retries_when_non_idempotent_opted_in(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession(
        [
            FakeResponse({"error": "gateway"}, status_code=503),
            FakeResponse({"ok": True}),
        ]
    )
    client = Client(
        base_url="https://example.test",
        session=session,
        retry_policy=RetryPolicy(retry_non_idempotent=True, backoff_factor=0, jitter=0),
    )

    async def sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(client, "_sleep_before_retry", sleep)

    assert await client.request("POST", "/api/v3/order", params={"market": "btctwd"}) == {"ok": True}
    assert len(session.calls) == 2


def test_request_sync_wrapper_runs_async_request() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(base_url="https://example.test", session=session)

    assert client.request_sync("GET", "/api/v3/ping") == {"ok": True}
    assert session.calls[-1]["url"] == "https://example.test/api/v3/ping"


async def test_sync_wrappers_raise_inside_running_event_loop() -> None:
    client = Client(session=FakeSession(FakeResponse({"timestamp": 1678766175})))

    with pytest.raises(RuntimeError, match="cannot run inside an active event loop"):
        client.timestamp_sync()


def test_default_sync_wrappers_use_fresh_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    sessions: list[FakeSession] = []

    def session_factory() -> FakeSession:
        session = FakeSession(FakeResponse({"timestamp": 1678766175}))
        sessions.append(session)
        return session

    monkeypatch.setattr("maicoin.v3.client.httpx.AsyncClient", session_factory)
    client = Client(base_url="https://example.test")

    assert client.timestamp_sync().timestamp == 1678766175
    assert client.timestamp_sync().timestamp == 1678766175

    assert len(sessions) == 2
    assert all(session.closed for session in sessions)


async def test_async_context_manager_closes_session() -> None:
    session = FakeSession(FakeResponse({}))

    async with Client(session=session):
        assert not session.closed

    assert session.closed
