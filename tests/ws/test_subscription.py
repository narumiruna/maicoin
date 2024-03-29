from maicoin.ws import Subscription


# https://maicoin.github.io/max-websocket-docs/#/public_orderbook?id=order-book-subscription
def test_subscription_book() -> None:
    d = {
        "channel": "book",
        "market": "btctwd",
        "depth": 1,  # optional
    }

    Subscription.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_trade?id=trade-subscription
def test_subscription_trade() -> None:
    d = {
        "channel": "trade",
        "market": "btctwd",
    }

    Subscription.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_ticker?id=ticker-subscription
def test_subscription_ticker() -> None:
    d = {
        "channel": "ticker",
        "market": "btctwd",
    }

    Subscription.model_validate(d)
