from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import cast

from maicoin.v3 import Client
from maicoin.v3 import ConvertOrder


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.status_code = 200
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, payload: object) -> None:
        self.response = FakeResponse(payload)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return self.response


def authenticated_client(session: FakeSession) -> Client:
    return Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )


def last_kwargs(session: FakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


def last_payload(session: FakeSession) -> Mapping[str, object]:
    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
    payload = base64.b64decode(headers["X-MAX-PAYLOAD"]).decode()
    return cast("Mapping[str, object]", json.loads(payload))


def convert_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "6322d9bd-736b-4f19-b862-829e75cae1ce",
        "from_currency": "btc",
        "from_amount": "0.01",
        "to_currency": "usdt",
        "to_amount": "289.13",
        "fee": "0.87",
        "fee_currency": "usdt",
        "fee_in_twd": "0.31",
        "created_at": 1704937708,
    }
    payload.update(overrides)
    return payload


def test_create_convert_constructs_authenticated_post_and_parses_payload() -> None:
    session = FakeSession(convert_payload())
    convert = authenticated_client(session).create_convert(
        from_currency="btc",
        to_currency="usdt",
        from_amount="0.01",
    )

    assert convert == ConvertOrder.model_validate(convert_payload())
    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/convert"
    assert last_kwargs(session)["json"] == {
        "from_currency": "btc",
        "to_currency": "usdt",
        "from_amount": "0.01",
    }
    assert last_payload(session)["path"] == "/api/v3/convert"


def test_convert_detail_constructs_authenticated_get_and_parses_payload() -> None:
    session = FakeSession(convert_payload())
    convert = authenticated_client(session).convert("6322d9bd-736b-4f19-b862-829e75cae1ce")

    assert convert.sn == "6322d9bd-736b-4f19-b862-829e75cae1ce"
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/convert"
    assert last_kwargs(session)["params"] == {"sn": "6322d9bd-736b-4f19-b862-829e75cae1ce"}


def test_converts_constructs_authenticated_get_and_parses_list() -> None:
    session = FakeSession([convert_payload()])
    converts = authenticated_client(session).converts(timestamp=1704937708, order="desc", limit=1)

    assert converts == [ConvertOrder.model_validate(convert_payload())]
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/converts"
    assert last_kwargs(session)["params"] == {"timestamp": 1704937708, "order": "desc", "limit": 1}
