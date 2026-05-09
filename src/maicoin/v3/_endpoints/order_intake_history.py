"""Order intake, order history, account, and private-trade REST v3 endpoints."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Sequence
from dataclasses import dataclass

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import iter_id_paginated
from maicoin.v3.models.orders import Account
from maicoin.v3.models.orders import Order
from maicoin.v3.models.orders import OrderSide
from maicoin.v3.models.orders import OrderType
from maicoin.v3.models.orders import PrivateTrade
from maicoin.v3.models.orders import UserInfo

INFO = EndpointSpec("GET", "/api/v3/info", auth=True)
ACCOUNTS = EndpointSpec("GET", "/api/v3/wallet/{wallet_type}/accounts", auth=True)
WALLET_TRADES = EndpointSpec("GET", "/api/v3/wallet/{wallet_type}/trades", auth=True)
OPEN_ORDERS = EndpointSpec("GET", "/api/v3/wallet/{wallet_type}/orders/open", auth=True)
CLOSED_ORDERS = EndpointSpec("GET", "/api/v3/wallet/{wallet_type}/orders/closed", auth=True)
ORDER_HISTORY = EndpointSpec("GET", "/api/v3/wallet/{wallet_type}/orders/history", auth=True)
ORDER = EndpointSpec("GET", "/api/v3/order", auth=True)
CREATE_ORDER = EndpointSpec("POST", "/api/v3/wallet/{wallet_type}/order", auth=True)
CANCEL_ORDER = EndpointSpec("DELETE", "/api/v3/order", auth=True)
CANCEL_ORDERS = EndpointSpec("DELETE", "/api/v3/wallet/{wallet_type}/orders", auth=True)
ORDER_TRADES = EndpointSpec("GET", "/api/v3/order/trades", auth=True)


@dataclass(frozen=True, slots=True)
class OrderIntakeHistoryEndpoints:
    """Authenticated account, trade, and order request/parse rules."""

    requester: RestRequester

    @property
    def endpoint(self) -> EndpointExecutor:
        return EndpointExecutor(self.requester)

    async def info(self) -> UserInfo:
        return await self.endpoint.model(INFO, UserInfo)

    async def accounts(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
        return await self.endpoint.model_list(
            ACCOUNTS,
            Account,
            {"currency": currency},
            path_params={"wallet_type": wallet_type},
        )

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
        return await self.endpoint.model_list(
            WALLET_TRADES,
            PrivateTrade,
            {"market": market, "timestamp": timestamp, "from_id": from_id, "order": order, "limit": limit},
            path_params={"wallet_type": wallet_type},
        )

    async def open_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        return await self.endpoint.model_list(
            OPEN_ORDERS,
            Order,
            {"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit},
            path_params={"wallet_type": wallet_type},
        )

    async def closed_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        return await self.endpoint.model_list(
            CLOSED_ORDERS,
            Order,
            {"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit},
            path_params={"wallet_type": wallet_type},
        )

    async def order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        return await self.endpoint.model_list(
            ORDER_HISTORY,
            Order,
            {"market": market, "from_id": from_id, "limit": limit},
            path_params={"wallet_type": wallet_type},
        )

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
        return await self.endpoint.model(ORDER, Order, {"id": order_id, "client_oid": client_oid})

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
        return await self.endpoint.model(
            CREATE_ORDER,
            Order,
            {
                "market": market,
                "side": side,
                "volume": volume,
                "price": price,
                "client_oid": client_oid,
                "stop_price": stop_price,
                "ord_type": ord_type,
                "group_id": group_id,
            },
            path_params={"wallet_type": wallet_type},
        )

    async def cancel_order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        return await self.endpoint.model(CANCEL_ORDER, Order, {"id": order_id, "client_oid": client_oid})

    async def cancel_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        side: OrderSide | str | None = None,
        group_id: int | None = None,
    ) -> list[Order]:
        return await self.endpoint.model_list(
            CANCEL_ORDERS,
            Order,
            {"market": market, "side": side, "group_id": group_id},
            path_params={"wallet_type": wallet_type},
        )

    async def order_trades(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        return await self.endpoint.model_list(
            ORDER_TRADES,
            PrivateTrade,
            {"order_id": order_id, "client_oid": client_oid},
        )
