"""Public market-data REST v3 endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3.models import Currency
from maicoin.v3.models import Depth
from maicoin.v3.models import KLine
from maicoin.v3.models import Market
from maicoin.v3.models import PublicTrade
from maicoin.v3.models import Ticker
from maicoin.v3.models import Timestamp

MARKETS = EndpointSpec("GET", "/api/v3/markets")
CURRENCIES = EndpointSpec("GET", "/api/v3/currencies")
TIMESTAMP = EndpointSpec("GET", "/api/v3/timestamp")
KLINE = EndpointSpec("GET", "/api/v3/k")
DEPTH = EndpointSpec("GET", "/api/v3/depth")
TRADES = EndpointSpec("GET", "/api/v3/trades")
TICKERS = EndpointSpec("GET", "/api/v3/tickers")
TICKER = EndpointSpec("GET", "/api/v3/ticker")


@dataclass(frozen=True, slots=True)
class PublicMarketDataEndpoints:
    """Public MAX market-data request and parsing rules."""

    requester: RestRequester

    @property
    def endpoint(self) -> EndpointExecutor:
        return EndpointExecutor(self.requester)

    async def markets(self) -> list[Market]:
        return await self.endpoint.model_list(MARKETS, Market)

    async def currencies(self) -> list[Currency]:
        return await self.endpoint.model_list(CURRENCIES, Currency)

    async def timestamp(self) -> Timestamp:
        return await self.endpoint.model(TIMESTAMP, Timestamp)

    async def kline(
        self,
        market: str,
        *,
        limit: int = 30,
        period: int = 1,
        timestamp: int | None = None,
    ) -> list[KLine]:
        payload = await self.endpoint.raw(
            KLINE,
            {"market": market, "limit": limit, "period": period, "timestamp": timestamp},
        )
        return [
            KLine(
                timestamp=int(str(row[0])),
                open=str(row[1]),
                high=str(row[2]),
                low=str(row[3]),
                close=str(row[4]),
                volume=str(row[5]),
            )
            for row in cast("list[Sequence[object]]", payload)
        ]

    async def depth(self, market: str, *, limit: int | None = None, sort_by_price: bool | None = None) -> Depth:
        return await self.endpoint.model(
            DEPTH,
            Depth,
            {"market": market, "limit": limit, "sort_by_price": sort_by_price},
        )

    async def trades(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        return await self.endpoint.model_list(
            TRADES,
            PublicTrade,
            {"market": market, "timestamp": timestamp, "limit": limit},
        )

    async def tickers(self, markets: Sequence[str]) -> list[Ticker]:
        return await self.endpoint.model_list(TICKERS, Ticker, {"markets[]": list(markets)})

    async def ticker(self, market: str) -> Ticker:
        return await self.endpoint.model(TICKER, Ticker, {"market": market})
