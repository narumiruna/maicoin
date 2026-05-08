from __future__ import annotations

import pytest

from maicoin.v3 import Client

pytestmark = pytest.mark.live


def test_timestamp(public_client: Client) -> None:
    timestamp = public_client.timestamp()

    assert timestamp.timestamp > 0


def test_markets_includes_live_market(public_client: Client, live_market: str) -> None:
    markets = public_client.markets()

    assert markets
    assert any(market.id == live_market for market in markets)


def test_currencies_returns_currency_models(public_client: Client) -> None:
    currencies = public_client.currencies()

    assert currencies
    assert all(currency.currency for currency in currencies)


def test_ticker(public_client: Client, live_market: str) -> None:
    ticker = public_client.ticker(live_market)

    assert ticker.market == live_market
    assert ticker.at > 0
    assert ticker.last is not None


def test_tickers(public_client: Client, live_market: str) -> None:
    tickers = public_client.tickers([live_market])

    assert len(tickers) == 1
    assert tickers[0].market == live_market


def test_depth(public_client: Client, live_market: str) -> None:
    depth = public_client.depth(live_market, limit=1)

    assert depth.timestamp > 0
    assert len(depth.asks) <= 1
    assert len(depth.bids) <= 1


def test_trades(public_client: Client, live_market: str) -> None:
    trades = public_client.trades(live_market, limit=1)

    assert len(trades) <= 1
    for trade in trades:
        assert trade.market == live_market
        assert trade.id > 0


def test_kline(public_client: Client, live_market: str) -> None:
    klines = public_client.kline(live_market, limit=1)

    assert len(klines) <= 1
    for kline in klines:
        assert kline.timestamp > 0
        assert kline.open
        assert kline.close
