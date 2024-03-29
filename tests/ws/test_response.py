from maicoin.ws.response import Response


# https://maicoin.github.io/max-websocket-docs/#/?id=error-response
def test_response_error() -> None:
    data = {"e": "error", "E": ["E-1004: invalid action"], "i": "client1", "T": 1678096431125}
    resp = Response.model_validate(data)

    assert resp.event == data["e"]
    assert resp.errors == data["E"]
    assert resp.id == data["i"]


# https://maicoin.github.io/max-websocket-docs/#/public_channels?id=subscribe-success-response
def test_response_subscribe_success() -> None:
    d = {
        "e": "subscribed",
        "s": [
            {"channel": "book", "market": "btctwd", "depth": 1},
            {"channel": "trade", "market": "btctwd"},
        ],
        "i": "client1",
        "T": 123456789,
    }
    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_channels?id=unsubscribe-success-response
def test_response_unsubscribe_success() -> None:
    d = {
        "e": "unsubscribed",
        "s": [
            {"channel": "book", "market": "btctwd", "depth": 1},
            {"channel": "trade", "market": "btctwd"},
        ],
        "i": "client1",
        "T": 123456789,
    }
    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_orderbook?id=snapshot
def test_response_book_snapshot() -> None:
    d = {
        "c": "book",
        "e": "snapshot",
        "M": "btcusdt",
        "a": [["5337.3", "0.1"]],
        "b": [["5333.3", "0.5"]],
        "T": 1591869939634,
    }
    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_orderbook?id=update
def test_response_book_update() -> None:
    d = {
        "c": "book",
        "e": "update",
        "M": "btcusdt",
        "a": [["5337.3", "0.01037"]],
        "b": [],
        "T": 1591869939634,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_trade?id=snapshot
def test_response_trade_snapshot() -> None:
    d = {
        "c": "trade",
        "e": "snapshot",
        "M": "btctwd",
        "t": [{"p": "5337.3", "v": "0.1", "T": 123456789, "tr": "up"}],
        "T": 123456789,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_trade?id=update
def test_response_trade_update() -> None:
    d = {
        "c": "trade",
        "e": "update",
        "M": "btctwd",
        "t": [{"p": "5337.3", "v": "0.1", "T": 123456789, "tr": "up"}],
        "T": 123456789,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_ticker?id=snapshot
def test_response_ticker_snapshot() -> None:
    d = {
        "c": "ticker",
        "e": "snapshot",
        "M": "btctwd",
        "tk": {
            "M": "btctwd",  # same as the above "M"
            "O": "280007.1",
            "H": "280017.2",
            "L": "280005.3",
            "C": "280004.5",
            "v": "71.01",
            "V": "71.01",  # volumes in BTC
        },
        "T": 123456789,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_ticker?id=update
def test_response_ticker_update() -> None:
    d = {
        "c": "ticker",
        "e": "update",
        "M": "btctwd",
        "tk": {
            "M": "btctwd",  # same as the above "M"
            "O": "280007.1",
            "H": "280017.2",
            "L": "280005.3",
            "C": "280004.5",
            "v": "71.01",
            "V": "71.01",  # volumes in BTC
        },
        "T": 123456789,
    }

    Response.model_validate(d)


def test_trade_response() -> None:
    data = {
        "c": "user",
        "e": "trade_snapshot",
        "t": [
            {
                "i": 77485757,
                "sa": "5cae57",
                "M": "usdcusdt",
                "sd": "ask",
                "p": "0.9995",
                "v": "8.01",
                "fn": "8.005995",
                "f": "0.01474438",
                "fc": "max",
                "fd": True,
                "T": 1711706400334,
                "TU": 1711706400649,
                "m": False,
                "oi": 7653999812,
            },
            {
                "i": 77457644,
                "sa": "5cae57",
                "M": "usdcusdt",
                "sd": "bid",
                "p": "1.0001",
                "v": "8.01",
                "fn": "8.010801",
                "f": "0.01475307",
                "fc": "max",
                "fd": True,
                "T": 1711684800324,
                "TU": 1711684800582,
                "m": False,
                "oi": 7650784793,
            },
        ],
        "T": 1711708692581,
    }
    Response.model_validate(data)
