"""Order intake, order history, account, and private-trade REST v3 endpoints."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import compact
from maicoin.v3._endpoints.base import iter_id_paginated
from maicoin.v3.models import Account
from maicoin.v3.models import Order
from maicoin.v3.models import OrderSide
from maicoin.v3.models import OrderType
from maicoin.v3.models import PrivateTrade
from maicoin.v3.models import UserInfo


@dataclass(frozen=True, slots=True)
class OrderIntakeHistoryEndpoints:
    """Authenticated account, trade, and order request/parse rules."""

    requester: RestRequester

    async def info(self) -> UserInfo:
        payload = await self.requester.request("GET", "/api/v3/info", auth=True)
        return UserInfo.model_validate(payload)

    async def accounts(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
        payload = await self.requester.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/accounts",
            params=compact({"currency": currency}),
            auth=True,
        )
        return [Account.model_validate(item) for item in cast("list[object]", payload)]

    async def wallet_trades(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        from_id: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[PrivateTrade]:
        payload = await self.requester.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/trades",
            params=compact(
                {"market": market, "timestamp": timestamp, "from_id": from_id, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [PrivateTrade.model_validate(item) for item in cast("list[object]", payload)]

    async def open_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        payload = await self.requester.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/open",
            params=compact({"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    async def closed_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        payload = await self.requester.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/closed",
            params=compact({"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    async def order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        payload = await self.requester.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/history",
            params=compact({"market": market, "from_id": from_id, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    async def iter_wallet_trades(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        from_id: int | None = None,
        order: str = "asc",
        page_limit: int = 100,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[PrivateTrade]:
        async def fetch_page(cursor: int | None, limit: int) -> Sequence[PrivateTrade]:
            return await self.wallet_trades(
                wallet_type=wallet_type,
                market=market,
                timestamp=timestamp,
                from_id=cursor,
                order=order,
                limit=limit,
            )

        async for trade in iter_id_paginated(
            fetch_page,
            lambda trade: trade.id,
            from_id=from_id,
            page_limit=page_limit,
            max_items=max_items,
            max_pages=max_pages,
        ):
            yield trade

    async def iter_order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        page_limit: int = 100,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Order]:
        async def fetch_page(cursor: int | None, limit: int) -> Sequence[Order]:
            return await self.order_history(market, wallet_type=wallet_type, from_id=cursor, limit=limit)

        async for order_item in iter_id_paginated(
            fetch_page,
            lambda order_item: order_item.id,
            from_id=from_id,
            page_limit=page_limit,
            max_items=max_items,
            max_pages=max_pages,
        ):
            yield order_item

    async def order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        payload = await self.requester.request(
            "GET",
            "/api/v3/order",
            params=compact({"id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return Order.model_validate(payload)

    async def create_order(
        self,
        market: str,
        side: OrderSide | str,
        volume: str,
        *,
        wallet_type: str = "spot",
        price: str | None = None,
        client_oid: str | None = None,
        stop_price: str | None = None,
        ord_type: OrderType | str | None = None,
        group_id: int | None = None,
    ) -> Order:
        payload = await self.requester.request(
            "POST",
            f"/api/v3/wallet/{wallet_type}/order",
            params=compact(
                {
                    "market": market,
                    "side": side,
                    "volume": volume,
                    "price": price,
                    "client_oid": client_oid,
                    "stop_price": stop_price,
                    "ord_type": ord_type,
                    "group_id": group_id,
                }
            ),
            auth=True,
        )
        return Order.model_validate(payload)

    async def cancel_order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        payload = await self.requester.request(
            "DELETE",
            "/api/v3/order",
            params=compact({"id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return Order.model_validate(payload)

    async def cancel_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        side: OrderSide | str | None = None,
        group_id: int | None = None,
    ) -> list[Order]:
        payload = await self.requester.request(
            "DELETE",
            f"/api/v3/wallet/{wallet_type}/orders",
            params=compact({"market": market, "side": side, "group_id": group_id}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    async def order_trades(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/order/trades",
            params=compact({"order_id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return [PrivateTrade.model_validate(item) for item in cast("list[object]", payload)]
