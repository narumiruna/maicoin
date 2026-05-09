"""Public market-data REST v3 endpoints."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import compact
from maicoin.v3.models import Currency
from maicoin.v3.models import Depth
from maicoin.v3.models import KLine
from maicoin.v3.models import Market
from maicoin.v3.models import PublicTrade
from maicoin.v3.models import Ticker
from maicoin.v3.models import Timestamp


@dataclass(frozen=True, slots=True)
class PublicMarketDataEndpoints:
    """Public MAX market-data request and parsing rules."""

    requester: RestRequester

    async def markets(self) -> list[Market]:
        payload = await self.requester.request("GET", "/api/v3/markets")
        return [Market.model_validate(item) for item in cast("list[object]", payload)]

    async def currencies(self) -> list[Currency]:
        payload = await self.requester.request("GET", "/api/v3/currencies")
        return [Currency.model_validate(item) for item in cast("list[object]", payload)]

    async def timestamp(self) -> Timestamp:
        payload = await self.requester.request("GET", "/api/v3/timestamp")
        return Timestamp.model_validate(payload)

    async def kline(
        self,
        market: str,
        *,
        limit: int = 30,
        period: int = 1,
        timestamp: int | None = None,
    ) -> list[KLine]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/k",
            params=compact({"market": market, "limit": limit, "period": period, "timestamp": timestamp}),
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
        payload = await self.requester.request(
            "GET",
            "/api/v3/depth",
            params=compact({"market": market, "limit": limit, "sort_by_price": sort_by_price}),
        )
        return Depth.model_validate(payload)

    async def trades(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/trades",
            params=compact({"market": market, "timestamp": timestamp, "limit": limit}),
        )
        return [PublicTrade.model_validate(item) for item in cast("list[object]", payload)]

    async def tickers(self, markets: Sequence[str]) -> list[Ticker]:
        payload = await self.requester.request("GET", "/api/v3/tickers", params={"markets[]": list(markets)})
        return [Ticker.model_validate(item) for item in cast("list[object]", payload)]

    async def ticker(self, market: str) -> Ticker:
        payload = await self.requester.request("GET", "/api/v3/ticker", params={"market": market})
        return Ticker.model_validate(payload)
