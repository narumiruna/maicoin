from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import cast

import pytest

from maicoin.v3 import Account
from maicoin.v3 import Client
from maicoin.v3 import Order
from maicoin.v3 import OrderSide
from maicoin.v3 import OrderState
from maicoin.v3 import OrderType
from maicoin.v3 import PrivateTrade
from maicoin.v3 import UserInfo

pytestmark = pytest.mark.anyio


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

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return self.response


class PagedFakeSession:
    def __init__(self, pages: list[object]) -> None:
        self.pages = pages
        self.calls: list[dict[str, object]] = []

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        page = self.pages[len(self.calls) - 1]
        return FakeResponse(page)


def last_kwargs(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


def last_payload(session: FakeSession) -> Mapping[str, object]:
    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
    payload = base64.b64decode(headers["X-MAX-PAYLOAD"]).decode()
    return cast("Mapping[str, object]", json.loads(payload))


def authenticated_client(session: FakeSession | PagedFakeSession) -> Client:
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


def trade_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
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
    payload.update(overrides)
    return payload


async def test_info_constructs_authenticated_request_and_parses_user_info() -> None:
    payload = {
        "email": "max@maicoin.com",
        "level": 0,
        "m_wallet_enabled": True,
        "current_vip_level": {
            "level": 0,
            "minimum_trading_volume": 0,
            "minimum_staking_volume": 0,
            "maker_fee": 0.0005,
            "taker_fee": 0.0015,
        },
        "next_vip_level": None,
    }
    session = FakeSession(payload)
    info = await authenticated_client(session).info()

    assert info == UserInfo.model_validate(payload)
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/info"
    assert last_payload(session) == {"nonce": 123456, "path": "/api/v3/info"}


async def test_accounts_constructs_authenticated_request_and_parses_accounts() -> None:
    session = FakeSession([{"currency": "twd", "balance": "100000.0", "locked": "5566.0", "staked": None}])
    client = authenticated_client(session)

    accounts = await client.accounts(currency="twd")

    assert accounts == [Account(currency="twd", balance="100000.0", locked="5566.0", staked=None)]
    assert session.calls[-1]["method"] == "GET"
    assert session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/accounts"
    assert last_kwargs(session)["params"] == {"nonce": 123456, "currency": "twd"}
    assert last_payload(session) == {
        "nonce": 123456,
        "currency": "twd",
        "path": "/api/v3/wallet/spot/accounts",
    }


async def test_open_closed_and_history_orders_parse_order_models() -> None:
    expected_order = Order.model_validate(order_payload())

    open_session = FakeSession([order_payload()])
    assert await authenticated_client(open_session).open_orders(market="ethtwd", limit=1) == [expected_order]
    assert open_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/orders/open"
    assert last_kwargs(open_session)["params"] == {"nonce": 123456, "market": "ethtwd", "limit": 1}

    closed_session = FakeSession([order_payload(state="done")])
    closed_orders = await authenticated_client(closed_session).closed_orders(wallet_type="m")
    assert closed_orders[0].state == "done"
    assert closed_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/orders/closed"

    history_session = FakeSession([order_payload()])
    history = await authenticated_client(history_session).order_history("ethtwd", from_id=10, limit=50)
    assert history == [expected_order]
    assert last_kwargs(history_session)["params"] == {"nonce": 123456, "market": "ethtwd", "from_id": 10, "limit": 50}


async def test_wallet_trades_constructs_authenticated_request_and_parses_private_trades() -> None:
    payload = trade_payload()
    session = FakeSession([payload])
    trades = await authenticated_client(session).wallet_trades(market="ethtwd", from_id=68444, order="asc", limit=1)

    assert trades == [PrivateTrade.model_validate(payload)]
    assert session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/trades"
    assert last_kwargs(session)["params"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "from_id": 68444,
        "order": "asc",
        "limit": 1,
    }
    assert last_payload(session)["path"] == "/api/v3/wallet/spot/trades"


async def test_iter_wallet_trades_advances_from_id_and_stops_at_max_items() -> None:
    session = PagedFakeSession(
        [
            [trade_payload(id=1), trade_payload(id=2)],
            [trade_payload(id=2), trade_payload(id=3)],
        ]
    )
    client = authenticated_client(session)

    trades = [trade async for trade in client.iter_wallet_trades(market="ethtwd", from_id=0, page_limit=2, max_items=3)]

    assert [trade.id for trade in trades] == [1, 2, 3]
    assert cast("Mapping[str, object]", session.calls[0]["kwargs"])["params"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "from_id": 0,
        "order": "asc",
        "limit": 2,
    }
    assert cast("Mapping[str, object]", session.calls[1]["kwargs"])["params"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "from_id": 2,
        "order": "asc",
        "limit": 2,
    }


async def test_iter_order_history_advances_from_id_until_short_page() -> None:
    session = PagedFakeSession(
        [
            [order_payload(id=1), order_payload(id=2)],
            [order_payload(id=3)],
        ]
    )
    client = authenticated_client(session)

    orders = [order async for order in client.iter_order_history("ethtwd", from_id=0, page_limit=2)]

    assert [order.id for order in orders] == [1, 2, 3]
    assert cast("Mapping[str, object]", session.calls[0]["kwargs"])["params"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "from_id": 0,
        "limit": 2,
    }
    assert cast("Mapping[str, object]", session.calls[1]["kwargs"])["params"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "from_id": 2,
        "limit": 2,
    }


async def test_iter_order_history_respects_max_pages() -> None:
    session = PagedFakeSession(
        [
            [order_payload(id=1), order_payload(id=2)],
            [order_payload(id=3), order_payload(id=4)],
        ]
    )
    client = authenticated_client(session)

    orders = [order async for order in client.iter_order_history("ethtwd", page_limit=2, max_pages=1)]

    assert [order.id for order in orders] == [1, 2]
    assert len(session.calls) == 1


async def test_order_lookup_and_order_trades_construct_requests() -> None:
    order_session = FakeSession(order_payload())
    order = await authenticated_client(order_session).order(order_id=87)

    assert order.id == 87
    assert order.side is OrderSide.BUY
    assert order.state is OrderState.WAIT
    assert order.ord_type is OrderType.LIMIT
    assert order_session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(order_session)["params"] == {"nonce": 123456, "id": 87}

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
    trades = await authenticated_client(trade_session).order_trades(client_oid="client-1")

    assert trades == [PrivateTrade.model_validate(trade_payload)]
    assert trade_session.calls[-1]["url"] == "https://example.test/api/v3/order/trades"
    assert last_kwargs(trade_session)["params"] == {"nonce": 123456, "client_oid": "client-1"}


async def test_create_and_cancel_order_send_authenticated_json_body() -> None:
    create_session = FakeSession(order_payload())
    created = await authenticated_client(create_session).create_order(
        "ethtwd",
        OrderSide.BUY,
        "0.2658",
        price="21499.0",
        ord_type=OrderType.LIMIT,
        client_oid="client-1",
    )

    assert created.id == 87
    assert create_session.calls[-1]["method"] == "POST"
    assert create_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/order"
    assert last_kwargs(create_session)["json"] == {
        "nonce": 123456,
        "market": "ethtwd",
        "side": "buy",
        "volume": "0.2658",
        "price": "21499.0",
        "client_oid": "client-1",
        "ord_type": "limit",
    }
    assert last_payload(create_session)["path"] == "/api/v3/wallet/spot/order"

    cancel_session = FakeSession(order_payload(state="cancel"))
    cancelled_order = await authenticated_client(cancel_session).cancel_order(order_id=87)
    assert cancelled_order.state == "cancel"
    assert cancel_session.calls[-1]["method"] == "DELETE"
    assert cancel_session.calls[-1]["url"] == "https://example.test/api/v3/order"
    assert last_kwargs(cancel_session)["json"] == {"nonce": 123456, "id": 87}

    cancel_all_session = FakeSession([order_payload(state="cancel")])
    cancelled = await authenticated_client(cancel_all_session).cancel_orders(market="ethtwd", side="buy")
    assert cancelled[0].state == "cancel"
    assert cancel_all_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/spot/orders"
    assert last_kwargs(cancel_all_session)["json"] == {"nonce": 123456, "market": "ethtwd", "side": "buy"}
