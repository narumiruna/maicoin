from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from maicoin.v3 import Client
from maicoin.v3 import Depth
from maicoin.v3 import InterestRate
from maicoin.v3 import KLine
from maicoin.v3 import Market
from maicoin.v3 import Ticker


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


def last_params(session: FakeSession) -> Mapping[str, object]:
    kwargs = cast("Mapping[str, object]", session.calls[-1]["kwargs"])
    return cast("Mapping[str, object]", kwargs["params"])


def test_markets_returns_market_models() -> None:
    session = FakeSession(
        [
            {
                "id": "btctwd",
                "status": "active",
                "base_unit": "btc",
                "base_unit_precision": 8,
                "min_base_amount": 0.0004,
                "quote_unit": "twd",
                "quote_unit_precision": 1,
                "min_quote_amount": 250,
                "m_wallet_supported": True,
            }
        ]
    )
    client = Client(base_url="https://example.test", session=session)

    markets = client.markets()

    assert markets == [
        Market(
            id="btctwd",
            status="active",
            base_unit="btc",
            base_unit_precision=8,
            min_base_amount=0.0004,
            quote_unit="twd",
            quote_unit_precision=1,
            min_quote_amount=250,
            m_wallet_supported=True,
        )
    ]
    assert session.calls[-1]["url"] == "https://example.test/api/v3/markets"


def test_currencies_returns_currency_models() -> None:
    session = FakeSession(
        [
            {
                "currency": "usdt",
                "type": "crypto",
                "precision": 8,
                "m_wallet_supported": True,
                "m_wallet_mortgageable": True,
                "m_wallet_borrowable": True,
                "min_borrow_amount": "0.001",
                "networks": [
                    {
                        "token_contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                        "precision": 8,
                        "id": "trc20usdt",
                        "network_protocol": "tron-trc20",
                        "network_congested": False,
                        "deposit_confirmations": 3,
                        "withdrawal_fee": 0.0005,
                        "min_withdrawal_amount": 0.001,
                        "withdrawal_enabled": True,
                        "deposit_enabled": True,
                        "need_memo": False,
                    }
                ],
                "staking": None,
            }
        ]
    )
    client = Client(base_url="https://example.test", session=session)

    currencies = client.currencies()

    assert currencies[0].currency == "usdt"
    assert currencies[0].networks[0].id == "trc20usdt"
    assert currencies[0].staking is None


def test_timestamp_returns_timestamp_model() -> None:
    client = Client(base_url="https://example.test", session=FakeSession({"timestamp": 1678766175}))

    assert client.timestamp().timestamp == 1678766175


def test_kline_constructs_params_and_parses_rows() -> None:
    session = FakeSession([[1678766100, "1", "2", "0.5", "1.5", "42"]])
    client = Client(base_url="https://example.test", session=session)

    klines = client.kline("btctwd", limit=1, period=5, timestamp=1678766100)

    assert klines == [KLine(timestamp=1678766100, open="1", high="2", low="0.5", close="1.5", volume="42")]
    assert last_params(session) == {"market": "btctwd", "limit": 1, "period": 5, "timestamp": 1678766100}


def test_depth_constructs_params_and_parses_depth() -> None:
    session = FakeSession(
        {
            "timestamp": 1778249163,
            "last_update_version": 1778220148899,
            "last_update_id": 556021,
            "asks": [["2520230.1", "0.00128053"]],
            "bids": [["2520028.3", "0.11903796"]],
        }
    )
    client = Client(base_url="https://example.test", session=session)

    depth = client.depth("btctwd", limit=1, sort_by_price=True)

    assert depth == Depth(
        timestamp=1778249163,
        last_update_version=1778220148899,
        last_update_id=556021,
        asks=[("2520230.1", "0.00128053")],
        bids=[("2520028.3", "0.11903796")],
    )
    assert last_params(session) == {"market": "btctwd", "limit": 1, "sort_by_price": True}


def test_trades_constructs_params_and_parses_trades() -> None:
    session = FakeSession(
        [
            {
                "id": 68444,
                "price": "21499.0",
                "volume": "0.2658",
                "funds": "5714.4",
                "market": "ethtwd",
                "side": "bid",
                "created_at": 1521726960357,
            }
        ]
    )
    client = Client(base_url="https://example.test", session=session)

    trades = client.trades("ethtwd", timestamp=1521726960357, limit=1)

    assert trades[0].id == 68444
    assert trades[0].side == "bid"
    assert last_params(session) == {"market": "ethtwd", "timestamp": 1521726960357, "limit": 1}


def test_tickers_uses_bracket_array_param_and_parses_tickers() -> None:
    ticker_payload = {
        "market": "btctwd",
        "at": 1531905257,
        "buy": "200000.0",
        "buy_vol": "0.01",
        "sell": "200001.0",
        "sell_vol": "0.02",
        "open": "199000.0",
        "low": "198000.0",
        "high": "201000.0",
        "last": "200500.0",
        "vol": "10.0",
        "vol_in_btc": "10.0",
        "vol_in_quote": "2005000.0",
    }
    session = FakeSession([ticker_payload])
    client = Client(base_url="https://example.test", session=session)

    tickers = client.tickers(["btctwd", "ethusdt"])

    assert tickers == [Ticker.model_validate(ticker_payload)]
    assert last_params(session) == {"markets[]": ["btctwd", "ethusdt"]}


def test_ticker_constructs_params_and_parses_ticker() -> None:
    session = FakeSession(
        {
            "market": "btctwd",
            "at": 1531905257,
            "buy": "200000.0",
            "buy_vol": "0.01",
            "sell": "200001.0",
            "sell_vol": "0.02",
            "open": "199000.0",
            "low": "198000.0",
            "high": "201000.0",
            "last": "200500.0",
            "vol": "10.0",
            "vol_in_btc": "10.0",
            "vol_in_quote": "2005000.0",
        }
    )
    client = Client(base_url="https://example.test", session=session)

    ticker = client.ticker("btctwd")

    assert ticker.market == "btctwd"
    assert last_params(session) == {"market": "btctwd"}


def test_m_wallet_public_methods_parse_payloads() -> None:
    assert Client(session=FakeSession({"btcusdt": "79848.60666667"})).m_wallet_index_prices() == {
        "btcusdt": "79848.60666667"
    }
    assert Client(session=FakeSession({"btc": "10.67520286"})).m_wallet_limits() == {"btc": "10.67520286"}

    rates = Client(
        session=FakeSession({"btc": {"hourly_interest_rate": "0.00000126", "next_hourly_interest_rate": "0.00000126"}})
    ).m_wallet_interest_rates()
    assert rates == {"btc": InterestRate(hourly_interest_rate="0.00000126", next_hourly_interest_rate="0.00000126")}


def test_m_wallet_historical_index_prices_constructs_params_and_parses_prices() -> None:
    session = FakeSession([{"timestamp": "1644572610000", "price": "43497.56666666"}])
    client = Client(base_url="https://example.test", session=session)

    prices = client.m_wallet_historical_index_prices("btcusdt", start_time=1644572610000, end_time=1644572670000)

    assert prices[0].timestamp == "1644572610000"
    assert prices[0].price == "43497.56666666"
    assert last_params(session) == {"market": "btcusdt", "start_time": 1644572610000, "end_time": 1644572670000}
