import json

from maicoin.ws import Channel
from maicoin.ws import Filter
from maicoin.ws import Subscription
from maicoin.ws.request import Request


# https://maicoin.github.io/max-websocket-docs/#/public_channels?id=subscribe
def test_action_subscribe() -> None:
    d = {
        "action": "sub",
        "subscriptions": [
            {"channel": "book", "market": "btctwd", "depth": 1},
            {"channel": "trade", "market": "btctwd"},
        ],
        "id": "client1",
    }

    a = Request.model_validate(d)

    assert a.action == d["action"]


# https://maicoin.github.io/max-websocket-docs/#/public_channels?id=unsubscribe
def test_action_unsubscribe() -> None:
    d = {
        "action": "unsub",
        "subscription": [
            {"channel": "book", "market": "btctwd", "depth": 1},
            {"channel": "trade", "market": "btctwd"},
        ],
        "id": "client1",
    }
    Request.model_validate(d)


def test_unsubscribe_message_uses_documented_singular_subscription_key() -> None:
    request = Request.unsubscribe([Subscription(channel=Channel.BOOK, market="btctwd", depth=1)])
    message = json.loads(request.message())

    assert "subscription" in message
    assert "subscriptions" not in message


# https://maicoin.github.io/max-websocket-docs/#/authentication?id=subscription
def test_action_auth() -> None:
    d = {
        "action": "auth",
        "apiKey": "...",
        "nonce": 1591690054859,
        "signature": "....",
        "id": "client-id",
    }

    Request.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/authentication?id=subscription-with-filters
def test_action_auth_filters() -> None:
    d = {
        "action": "auth",
        "apiKey": "...",
        "nonce": 1591690054859,
        "signature": "....",
        "id": "client-id",
        "filters": ["order", "trade", "fast_trade_update"],  # ignore account update
    }

    request = Request.model_validate(d)

    assert request.filters == [Filter.ORDER, Filter.TRADE, Filter.FAST_TRADE_UPDATE]


def test_auth_message_can_request_private_filters() -> None:
    request = Request.auth("key", "secret", filters=[Filter.ORDER, Filter.FAST_TRADE_UPDATE])
    message = json.loads(request.message())

    assert message["filters"] == ["order", "fast_trade_update"]


def test_action_auth_mwallet_filters() -> None:
    d = {
        "action": "auth",
        "apiKey": "...",
        "nonce": 1591690054859,
        "signature": "....",
        "id": "client-id",
        "filters": [
            "mwallet_order",
            "mwallet_trade",
            "mwallet_fast_trade_update",
            "mwallet_account",
            "ad_ratio",
            "borrowing",
        ],
    }

    request = Request.model_validate(d)

    assert request.filters == [
        Filter.MWALLET_ORDER,
        Filter.MWALLET_TRADE,
        Filter.MWALLET_FAST_TRADE_UPDATE,
        Filter.MWALLET_ACCOUNT,
        Filter.AD_RATIO,
        Filter.BORROWING,
    ]
