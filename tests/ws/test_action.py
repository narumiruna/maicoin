from maicoin.ws.action import Action


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

    a = Action.model_validate(d)

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
    Action.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/authentication?id=subscription
def test_action_auth() -> None:
    d = {
        "action": "auth",
        "apiKey": "...",
        "nonce": 1591690054859,
        "signature": "....",
        "id": "client-id",
    }

    Action.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/authentication?id=subscription-with-filters
def test_action_auth_filters() -> None:
    d = {
        "action": "auth",
        "apiKey": "...",
        "nonce": 1591690054859,
        "signature": "....",
        "id": "client-id",
        "filters": ["order", "trade"],  # ignore account update
    }

    Action.model_validate(d)
