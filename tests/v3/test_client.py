from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import cast

import pytest

from maicoin.v3.client import Client
from maicoin.v3.errors import MaxAPIError
from maicoin.v3.errors import MaxHTTPError


class FakeResponse:
    def __init__(self, payload: object, *, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []
        self.closed = False

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return self.response

    async def aclose(self) -> None:
        self.closed = True


def last_kwargs(session: FakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


def test_get_request_sends_params_as_query_params() -> None:
    session = FakeSession(FakeResponse([{"id": "btctwd"}]))
    client = Client(base_url="https://example.test", session=session)

    assert asyncio.run(client.request("GET", "/api/v3/markets", params={"foo": "bar"})) == [{"id": "btctwd"}]

    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/markets"
    assert last_kwargs(session)["params"] == {"foo": "bar"}
    assert "json" not in last_kwargs(session)


def test_post_request_sends_params_as_json_body() -> None:
    session = FakeSession(FakeResponse({"id": 1}))
    client = Client(base_url="https://example.test", session=session)

    assert asyncio.run(client.request("POST", "api/v3/order", params={"market": "btctwd"})) == {"id": 1}

    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(session)["json"] == {"market": "btctwd"}
    assert "params" not in last_kwargs(session)


def test_delete_request_sends_params_as_json_body() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(base_url="https://example.test", session=session)

    assert asyncio.run(client.request("DELETE", "/api/v3/order", params={"id": 1})) == {"ok": True}

    assert session.calls[-1]["method"] == "DELETE"
    assert last_kwargs(session)["json"] == {"id": 1}
    assert "params" not in last_kwargs(session)


def test_authenticated_request_adds_max_headers() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )

    asyncio.run(client.request("GET", "/api/v3/wallet/spot/accounts", params={"currency": "btc"}, auth=True))

    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
    assert headers["X-MAX-ACCESSKEY"] == "key"
    assert headers["X-MAX-PAYLOAD"] == (
        "eyJub25jZSI6MTIzNDU2LCJjdXJyZW5jeSI6ImJ0YyIsInBhdGgiOiIvYXBpL3YzL3dhbGxldC9zcG90L2FjY291bnRzIn0="
    )
    assert headers["X-MAX-SIGNATURE"] == "4347a83e4172fdf36e00c954deacfe143e77a360daef361106ff1ea852cceabe"
    assert headers["Content-Type"] == "application/json"
    assert last_kwargs(session)["params"] == {"nonce": 123456, "currency": "btc"}


def test_http_error_response_raises() -> None:
    client = Client(
        base_url="https://example.test",
        session=FakeSession(FakeResponse({"error": "invalid nonce"}, status_code=401)),
    )

    with pytest.raises(MaxHTTPError, match="invalid nonce"):
        asyncio.run(client.request("GET", "/api/v3/wallet/spot/accounts"))


def test_api_error_payload_raises() -> None:
    client = Client(base_url="https://example.test", session=FakeSession(FakeResponse({"error": "bad request"})))

    with pytest.raises(MaxAPIError, match="bad request"):
        asyncio.run(client.request("GET", "/api/v3/ticker"))


def test_authenticated_request_requires_credentials() -> None:
    client = Client(base_url="https://example.test", session=FakeSession(FakeResponse({})))

    with pytest.raises(ValueError, match="api_key and api_secret"):
        asyncio.run(client.request("GET", "/api/v3/wallet/spot/accounts", auth=True))


def test_request_sync_wrapper_runs_async_request() -> None:
    session = FakeSession(FakeResponse({"ok": True}))
    client = Client(base_url="https://example.test", session=session)

    assert client.request_sync("GET", "/api/v3/ping") == {"ok": True}
    assert session.calls[-1]["url"] == "https://example.test/api/v3/ping"


def test_async_context_manager_closes_session() -> None:
    async def run() -> FakeSession:
        session = FakeSession(FakeResponse({}))
        async with Client(session=session):
            assert not session.closed
        return session

    assert asyncio.run(run()).closed
