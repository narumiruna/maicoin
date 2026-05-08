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


def test_response_book_snapshot_preserves_string_levels_and_parses_update_ids() -> None:
    d = {
        "c": "book",
        "e": "snapshot",
        "M": "btcusdt",
        "a": [["5337.3000000000000001", "0.1"]],
        "b": [["5333.3", "0.5"]],
        "T": 1591869939634,
        "fi": 12141725,
        "li": 12141725,
        "v": 1725602999632,
    }

    response = Response.model_validate(d)

    assert response.asks == [["5337.3000000000000001", "0.1"]]
    assert response.first_update_id == 12141725
    assert response.last_update_id == 12141725
    assert response.version == 1725602999632


# https://maicoin.github.io/max-websocket-docs/#/public_mwallet_pool_quota?id=success-response
def test_response_mwallet_pool_quota() -> None:
    d = {
        "c": "pool_quota",
        "e": "snapshot",
        "qta": {
            "cu": "usdt",
            "av": "501353.81385068",
            "TU": 1641551141618,
        },
        "T": 1641772933737,
    }

    response = Response.model_validate(d)

    assert response.pool_quota is not None
    assert response.pool_quota.currency == "usdt"
    assert response.pool_quota.available == "501353.81385068"


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=fast-trade-response
def test_response_private_fast_trade_update() -> None:
    d = {
        "c": "user",
        "e": "fast_trade_update",
        "t": [
            {
                "i": 68444,
                "M": "ethtwd",
                "sd": "bid",
                "p": "21499.0",
                "v": "0.2658",
                "fn": "5714.4342",
                "T": 1659216053748,
                "TU": 1659216054046,
                "m": True,
                "oi": 3253823664,
            },
        ],
        "T": 1521726960357,
    }

    response = Response.model_validate(d)

    assert response.trades is not None
    assert response.trades[0].price == "21499.0"


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-order-response
def test_response_mwallet_order_snapshot() -> None:
    d = {
        "c": "user",
        "e": "mwallet_order_snapshot",
        "o": [
            {
                "i": 87,
                "sd": "bid",
                "ot": "limit",
                "p": "3320.49",
                "sp": None,
                "ap": "0.0",
                "v": "0.1",
                "rv": "0.1",
                "ev": "0.0",
                "S": "wait",
                "M": "ethusdt",
                "tc": 0,
                "T": 1633415952000,
                "TU": 1633415952701,
                "ci": "client-oid-1",
                "gi": 123,
            },
        ],
        "T": 1633415952715,
    }

    response = Response.model_validate(d)

    assert response.orders is not None
    assert response.orders[0].price == "3320.49"


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-trade-response
def test_response_mwallet_trade_update() -> None:
    d = {
        "c": "user",
        "e": "mwallet_trade_update",
        "t": [
            {
                "i": 78,
                "M": "ethusdt",
                "sd": "bid",
                "p": "3320.49",
                "v": "0.1",
                "f": "0.00015",
                "fc": "eth",
                "fn": "77.38889",
                "T": 1633359451377,
                "TU": 1633359451378,
                "m": False,
                "oi": 123,
            },
        ],
        "T": 1521726960357,
    }

    response = Response.model_validate(d)

    assert response.trades is not None
    assert response.trades[0].fee == "0.00015"


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-fast-trade-response
def test_response_mwallet_fast_trade_update() -> None:
    d = {
        "c": "user",
        "e": "mwallet_fast_trade_update",
        "t": [
            {
                "i": 78,
                "M": "ethusdt",
                "sd": "bid",
                "p": "3320.49",
                "v": "0.1",
                "fn": "77.38889",
                "T": 1633359451377,
                "TU": 1633359451378,
                "m": False,
                "oi": 123,
            },
        ],
        "T": 1521726960357,
    }

    Response.model_validate(d)


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-account-response
def test_response_mwallet_account_update_without_balance_update_time() -> None:
    d = {
        "c": "user",
        "e": "mwallet_account_update",
        "B": [
            {
                "cu": "btc",
                "av": "123.4",
                "l": "0.5",
                "stk": None,
            },
        ],
        "T": 1521726960357,
    }

    response = Response.model_validate(d)

    assert response.balances is not None
    assert response.balances[0].balance_updated_time is None


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-ad-ratio-response
def test_response_mwallet_ad_ratio_update() -> None:
    d = {
        "c": "user",
        "e": "ad_ratio_update",
        "ad": {
            "ad": "38.08306432",
            "as": "132071.22",
            "db": "3467.97775784",
            "idxp": [{"M": "btcusdt", "p": "63190.045"}],
            "TU": 1521726960300,
        },
        "T": 1521726960357,
    }

    response = Response.model_validate(d)

    assert response.m_wallet_ad_ratio is not None
    assert response.m_wallet_ad_ratio.index_prices[0].price == "63190.045"


# https://maicoin.github.io/max-websocket-docs/#/private_channels_mwallet?id=mwallet-borrowing-response
def test_response_mwallet_borrowing_update() -> None:
    d = {
        "c": "user",
        "e": "borrowing_update",
        "db": [
            {
                "cu": "usdt",
                "dbp": "500.0",
                "dbi": "0.00004488",
                "TU": 1521726960300,
            },
        ],
        "T": 1521726960357,
    }

    response = Response.model_validate(d)

    assert response.m_wallet_borrowings is not None
    assert response.m_wallet_borrowings[0].debt_interest == "0.00004488"
