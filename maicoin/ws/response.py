from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .balance import Balance
from .channel import Channel
from .kline import KLine
from .market_status import MarketStatus
from .order import Order
from .subscription import Subscription
from .ticker import Ticker
from .trade import Trade


class EventType(str, Enum):
    ERROR = "error"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    AUTHENTICATED = "authenticated"
    SNAPSHOT = "snapshot"
    UPDATE = "update"
    ORDER_SNAPSHOT = "order_snapshot"
    ORDER_UPDATE = "order_update"
    TRADE_SNAPSHOT = "trade_snapshot"
    TRADE_UPDATE = "trade_update"
    ACCOUNT_SNAPSHOT = "account_snapshot"
    ACCOUNT_UPDATE = "account_update"


# https://maicoin.github.io/max-websocket-docs/#/?id=response-key-alias
class Response(BaseModel):
    event: EventType = Field(validation_alias="e")
    created_at: datetime = Field(validation_alias="T")
    id: str | None = Field(default=None, validation_alias="i")
    errors: list[str] | None = Field(default=None, validation_alias="E")
    subscriptions: list[Subscription] | None = Field(default=None, validation_alias="s")
    channel: Channel | None = Field(default=None, validation_alias="c")
    balances: list[Balance] | None = Field(default=None, validation_alias="B")
    market: str | None = Field(default=None, validation_alias="M")
    asks: list[list[float]] | None = Field(default=None, validation_alias="a")
    bids: list[list[float]] | None = Field(default=None, validation_alias="b")
    orders: list[Order] | None = Field(default=None, validation_alias="o")
    ticker: Ticker | None = Field(default=None, validation_alias="tk")
    trades: list[Trade] | None = Field(default=None, validation_alias="t")
    currency: str | None = Field(default=None, validation_alias="cu")
    kline: KLine | None = Field(default=None, validation_alias="k")
    market_status: list[MarketStatus] | None = Field(default=None, validation_alias="ms")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> None:
        return datetime.fromtimestamp(int(t) / 1000)
