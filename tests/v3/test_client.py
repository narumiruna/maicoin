from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import pytest

from maicoin.v3.client import Client
from maicoin.v3.client import RetryPolicy
from maicoin.v3.errors import MaxAPIError
from maicoin.v3.errors import MaxHTTPError

pytestmark = pytest.mark.anyio


class FakeResponse:
    def __init__(self, payload: object, *, status_code: int = 200, headers: Mapping[str, str] | None = None) -> None:
        self.payload = payload
        self.status_code = status_code
        self.headers = dict(headers or {})
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse | list[FakeResponse]) -> None:
        self.responses = [response] if isinstance(response, FakeResponse) else response
        self.calls: list[dict[str, object]] = []
        self.closed = False

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if len(self.responses) == 1:
            return self.responses[0]
        return self.responses.pop(0)

    async def aclose(self) -> None:
        self.closed = True


def last_kwargs(session: FakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


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

    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
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
