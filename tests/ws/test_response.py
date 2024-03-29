from maicoin.ws.response import Response


# https://maicoin.github.io/max-websocket-docs/#/authentication?id=success-response
def test_response_auth_success() -> None:
    d = {
        "e": "authenticated",
        "i": "client-id",
        "T": 1591686735192,
    }

    Response.model_validate(d)


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
        "t": [
            {
                "p": "5337.3",
                "v": "0.1",
                "T": 123456789,
                "tr": "up",
            },
        ],
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


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=snapshot
def test_response_private_order_snapshot() -> None:
    d = {
        "c": "user",
        "e": "order_snapshot",
        "o": [
            {
                "i": 87,
                "sd": "bid",
                "ot": "limit",
                "p": "21499.0",
                "sp": "21499.0",
                "ap": "21499.0",
                "v": "0.2658",
                "rv": "0.0",
                "ev": "0.2658",
                "S": "done",
                "M": "ethtwd",
                "tc": 1,
                "T": 1659419048000,
                "TU": 1659419048406,
                "gi": 123,
                "ci": "client-oid-1",
            },
        ],
        "T": 1521726960357,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=update
def test_response_private_order_update() -> None:
    d = {
        "c": "user",
        "e": "order_update",
        "o": [
            {
                "i": 87,
                "sd": "bid",
                "ot": "limit",
                "p": "21499.0",
                "sp": "21499.0",
                "ap": "21499.0",
                "S": "done",
                "M": "ethtwd",
                "T": 1521726960123,
                "TU": 1521726960123,
                "v": "0.2658",
                "rv": "0.0",
                "ev": "0.2658",
                "tc": 1,
                "ci": "client-oid-1",
                "gi": 123,
            },
        ],
        "T": 1521726960357,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=snapshot-1
def test_response_private_trade_snapshot() -> None:
    d = {
        "c": "user",
        "e": "trade_snapshot",
        "t": [
            {
                "i": 68444,
                "M": "ethtwd",
                "sd": "bid",
                "p": "21499.0",
                "v": "0.2658",
                "f": "3.2",
                "fc": "twd",
                "fd": False,
                "fn": "5714.4342",
                "T": 1659216053748,
                "TU": 1659216054046,
                "m": True,
                "oi": 3253823664,
            },
        ],
        "T": 1659412100259,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=snapshot-2
def test_response_private_account_snapshot() -> None:
    d = {
        "c": "user",
        "e": "account_snapshot",
        "B": [
            {
                "cu": "btc",
                "av": "123.4",
                "l": "0.5",
                "stk": None,
                "TU": 1659390246343,
            },
        ],
        "T": 1659412100181,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=update-2
def test_response_private_account_update() -> None:
    d = {
        "c": "user",
        "e": "account_update",
        "B": [
            {
                "cu": "btc",
                "av": "123.4",
                "l": "0.5",
                "stk": None,
                "TU": 1659390246343,
            }
        ],
        "T": 1659412100181,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=snapshot
def test_response_private_kline_snapshot() -> None:
    d = {
        "c": "kline",
        "M": "ethusdt",
        "e": "snapshot",
        "T": 1684743644396,
        "k": {
            "ST": 1684743600000,
            "ET": 1684743659999,
            "M": "ethusdt",
            "R": "1m",
            "O": "1815.11",
            "H": "1815.11",
            "L": "1815.11",
            "C": "1815.11",
            "v": "0",
            "ti": 58684589,
            "x": False,
        },
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=update
def test_response_private_kline_update() -> None:
    d = {
        "c": "kline",
        "M": "ethusdt",
        "e": "update",
        "T": 1684743650395,
        "k": {
            "ST": 1684743600000,
            "ET": 1684743659999,
            "M": "ethusdt",
            "R": "1m",
            "O": "1815.11",
            "H": "1815.11",
            "L": "1815.11",
            "C": "1815.11",
            "v": "0",
            "ti": 58684589,
            "x": False,
        },
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_market_status?id=snapshot
def test_response_market_status_snapshot() -> None:
    d = {
        "c": "market_status",
        "e": "snapshot",
        "ms": [
            {
                "M": "btctwd",
                "st": "active",
                "bu": "btc",
                "bup": 8,
                "mba": 0.0004,
                "qu": "twd",
                "qup": 1,
                "mqa": 250,
                "mws": True,
            },
        ],
        "T": 1659428472313,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/public_market_status?id=update
def test_response_market_status_update() -> None:
    d = {
        "c": "market_status",
        "e": "update",
        "ms": [
            {
                "M": "btctwd",
                "st": "active",
                "bu": "btc",
                "bup": 8,
                "mba": 0.0004,
                "qu": "twd",
                "qup": 1,
                "mqa": 250,
                "mws": True,
            }
        ],
        "T": 1659428472313,
    }

    Response.model_validate(d)
