from __future__ import annotations

from datetime import UTC
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from maicoin.ws.balance import Balance
from maicoin.ws.channel import Channel
from maicoin.ws.kline import KLine
from maicoin.ws.m_wallet import MWalletADRatio
from maicoin.ws.m_wallet import MWalletBorrowing
from maicoin.ws.m_wallet import PoolQuota
from maicoin.ws.market_status import MarketStatus
from maicoin.ws.order import Order
from maicoin.ws.subscription import Subscription
from maicoin.ws.ticker import Ticker
from maicoin.ws.trade import Trade


class Event(StrEnum):
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
    FAST_TRADE_UPDATE = "fast_trade_update"
    MWALLET_ORDER_SNAPSHOT = "mwallet_order_snapshot"
    MWALLET_ORDER_UPDATE = "mwallet_order_update"
    MWALLET_TRADE_SNAPSHOT = "mwallet_trade_snapshot"
    MWALLET_TRADE_UPDATE = "mwallet_trade_update"
    MWALLET_FAST_TRADE_UPDATE = "mwallet_fast_trade_update"
    MWALLET_ACCOUNT_SNAPSHOT = "mwallet_account_snapshot"
    MWALLET_ACCOUNT_UPDATE = "mwallet_account_update"
    AD_RATIO_SNAPSHOT = "ad_ratio_snapshot"
    AD_RATIO_UPDATE = "ad_ratio_update"
    BORROWING_SNAPSHOT = "borrowing_snapshot"
    BORROWING_UPDATE = "borrowing_update"


# https://maicoin.github.io/max-websocket-docs/#/?id=response-key-alias
class Response(BaseModel):
    event: Event = Field(validation_alias="e")
    created_at: datetime = Field(validation_alias="T")
    id: str | None = Field(default=None, validation_alias="i")
    errors: list[str] | None = Field(default=None, validation_alias="E")
    subscriptions: list[Subscription] | None = Field(default=None, validation_alias="s")
    channel: Channel | None = Field(default=None, validation_alias="c")
    balances: list[Balance] | None = Field(default=None, validation_alias="B")
    market: str | None = Field(default=None, validation_alias="M")
    asks: list[list[str]] | None = Field(default=None, validation_alias="a")
    bids: list[list[str]] | None = Field(default=None, validation_alias="b")
    first_update_id: int | None = Field(default=None, validation_alias="fi")
    last_update_id: int | None = Field(default=None, validation_alias="li")
    version: int | None = Field(default=None, validation_alias="v")
    orders: list[Order] | None = Field(default=None, validation_alias="o")
    ticker: Ticker | None = Field(default=None, validation_alias="tk")
    trades: list[Trade] | None = Field(default=None, validation_alias="t")
    currency: str | None = Field(default=None, validation_alias="cu")
    kline: KLine | None = Field(default=None, validation_alias="k")
    market_status: list[MarketStatus] | None = Field(default=None, validation_alias="ms")
    pool_quota: PoolQuota | None = Field(default=None, validation_alias="qta")
    m_wallet_ad_ratio: MWalletADRatio | None = Field(default=None, validation_alias="ad")
    m_wallet_borrowings: list[MWalletBorrowing] | None = Field(default=None, validation_alias="db")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)
