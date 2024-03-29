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
