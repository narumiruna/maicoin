from __future__ import annotations

import pytest

from maicoin.v3 import ConvertOrder
from tests.v3.helpers import FakeSession
from tests.v3.helpers import authenticated_client
from tests.v3.helpers import last_json
from tests.v3.helpers import last_kwargs
from tests.v3.helpers import last_payload

pytestmark = pytest.mark.anyio


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


async def test_create_convert_constructs_authenticated_post_and_parses_payload() -> None:
    session = FakeSession(convert_payload())
    convert = await authenticated_client(session).create_convert(
        from_currency="btc",
        to_currency="usdt",
        from_amount="0.01",
    )

    assert convert == ConvertOrder.model_validate(convert_payload())
    assert session.calls[-1]["method"] == "POST"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/convert"
    assert last_json(session) == {
        "nonce": 123456,
        "from_currency": "btc",
        "to_currency": "usdt",
        "from_amount": "0.01",
    }
    assert last_payload(session)["path"] == "/api/v3/convert"


async def test_convert_detail_constructs_authenticated_get_and_parses_payload() -> None:
    session = FakeSession(convert_payload())
    convert = await authenticated_client(session).convert("6322d9bd-736b-4f19-b862-829e75cae1ce")

    assert convert.sn == "6322d9bd-736b-4f19-b862-829e75cae1ce"
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/convert"
    assert last_kwargs(session)["params"] == {"nonce": 123456, "sn": "6322d9bd-736b-4f19-b862-829e75cae1ce"}


async def test_converts_constructs_authenticated_get_and_parses_list() -> None:
    session = FakeSession([convert_payload()])
    converts = await authenticated_client(session).converts(timestamp=1704937708, order="desc", limit=1)

    assert converts == [ConvertOrder.model_validate(convert_payload())]
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/converts"
    assert last_kwargs(session)["params"] == {"nonce": 123456, "timestamp": 1704937708, "order": "desc", "limit": 1}
