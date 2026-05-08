from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import cast

from maicoin.v3 import Account
from maicoin.v3 import Client
from maicoin.v3 import Order
from maicoin.v3 import PrivateTrade


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


def last_kwargs(session: FakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


def last_payload(session: FakeSession) -> Mapping[str, object]:
    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
    payload = base64.b64decode(headers["X-MAX-PAYLOAD"]).decode()
    return cast("Mapping[str, object]", json.loads(payload))


def authenticated_client(session: FakeSession) -> Client:
    return Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )


def order_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": 87,
        "wallet_type": "spot",
        "market": "ethtwd",
        "client_oid": "client-1",
        "group_id": 1,
        "side": "buy",
        "state": "wait",
        "ord_type": "limit",
        "price": "21499.0",
        "stop_price": None,
        "avg_price": "0.0",
        "volume": "0.2658",
        "remaining_volume": "0.2658",
        "executed_volume": "0.0",
        "trades_count": 0,
        "created_at": 1521726960123,
        "updated_at": 1521726960123,
    }
    payload.update(overrides)
    return payload


def test_accounts_constructs_authenticated_request_and_parses_accounts() -> None:
    session = FakeSession([{"currency": "twd", "balance": "100000.0", "locked": "5566.0", "staked": None}])
    client = authenticated_client(session)

    accounts = client.accounts(currency="twd")

    assert accounts == [Account(currency="twd", balance="100000.0", locked="5566.0", staked=None)]
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/accounts"
    assert last_kwargs(session)["params"] == {"currency": "twd"}
    assert last_payload(session) == {
        "nonce": 123456,
        "currency": "twd",
        "path": "/api/v3/wallet/spot/accounts",
    }


def test_open_closed_and_history_orders_parse_order_models() -> None:
    expected_order = Order.model_validate(order_payload())

    open_session = FakeSession([order_payload()])
    assert authenticated_client(open_session).open_orders(market="ethtwd", limit=1) == [expected_order]
    assert open_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/orders/open"
    assert last_kwargs(open_session)["params"] == {"market": "ethtwd", "limit": 1}

    closed_session = FakeSession([order_payload(state="done")])
    assert authenticated_client(closed_session).closed_orders(wallet_type="m")[0].state == "done"
    assert closed_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/orders/closed"

    history_session = FakeSession([order_payload()])
    history = authenticated_client(history_session).order_history("ethtwd", from_id=10, limit=50)
    assert history == [expected_order]
    assert last_kwargs(history_session)["params"] == {"market": "ethtwd", "from_id": 10, "limit": 50}


def test_order_lookup_and_order_trades_construct_requests() -> None:
    order_session = FakeSession(order_payload())
    order = authenticated_client(order_session).order(order_id=87)

    assert order.id == 87
    assert order_session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(order_session)["params"] == {"id": 87}

    trade_payload = {
        "id": 68444,
        "order_id": 87,
        "wallet_type": "spot",
        "price": "21499.0",
        "volume": "0.2658",
        "funds": "5714.4",
        "market": "ethtwd",
        "market_name": "ETH/TWD",
        "side": "bid",
        "fee": "0.00001",
        "fee_currency": "usdt",
        "fee_discounted": False,
        "liquidity": "taker",
        "created_at": 1521726960357,
    }
    trade_session = FakeSession([trade_payload])
    trades = authenticated_client(trade_session).order_trades(client_oid="client-1")

    assert trades == [PrivateTrade.model_validate(trade_payload)]
    assert trade_session.calls[-1]["url"] == "https://example.test/api/v3/order/trades"
    assert last_kwargs(trade_session)["params"] == {"client_oid": "client-1"}


def test_create_and_cancel_order_send_authenticated_json_body() -> None:
    create_session = FakeSession(order_payload())
    created = authenticated_client(create_session).create_order(
        "ethtwd",
        "buy",
        "0.2658",
        price="21499.0",
        ord_type="limit",
        client_oid="client-1",
    )

    assert created.id == 87
    assert create_session.calls[-1]["method"] == "POST"
    assert create_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/order"
    assert last_kwargs(create_session)["json"] == {
        "market": "ethtwd",
        "side": "buy",
        "volume": "0.2658",
        "price": "21499.0",
        "client_oid": "client-1",
        "ord_type": "limit",
    }
    assert last_payload(create_session)["path"] == "/api/v3/wallet/spot/order"

    cancel_session = FakeSession(order_payload(state="cancel"))
    assert authenticated_client(cancel_session).cancel_order(order_id=87).state == "cancel"
    assert cancel_session.calls[-1]["method"] == "DELETE"
    assert cancel_session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(cancel_session)["json"] == {"id": 87}

    cancel_all_session = FakeSession([order_payload(state="cancel")])
    cancelled = authenticated_client(cancel_all_session).cancel_orders(market="ethtwd", side="buy")
    assert cancelled[0].state == "cancel"
    assert cancel_all_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/orders"
    assert last_kwargs(cancel_all_session)["json"] == {"market": "ethtwd", "side": "buy"}
