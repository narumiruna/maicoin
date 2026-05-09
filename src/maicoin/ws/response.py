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
    """Event names sent in the `e` field of every MAX WebSocket response.

    Snapshot events deliver the full current state on (re)subscribe; update
    events deliver incremental changes after that. Lifecycle events
    (`error`, `subscribed`, `unsubscribed`, `authenticated`) confirm
    request handling.
    """

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


class Response(BaseModel):
    """A single message decoded from the MAX WebSocket connection.

    The MAX wire format uses one-letter aliases (`e`, `T`, `M`, …) to keep
    payloads small. This model exposes readable Python field names while
    preserving the wire aliases via `validation_alias` so it parses raw MAX
    JSON directly.

    See the [MAX response key alias reference](https://maicoin.github.io/max-websocket-docs/#/?id=response-key-alias).
    Inspect `event` to dispatch on message type, and read whichever payload
    field matches that event (`ticker`, `trades`, `orders`, …).
    """

    event: Event = Field(validation_alias="e")
    """Event type. Drives which payload fields are populated."""
    created_at: datetime = Field(validation_alias="T")
    """Server timestamp, converted from millisecond UNIX time."""
    id: str | None = Field(default=None, validation_alias="i")
    """Echoed request id for `subscribed` / `unsubscribed` / `authenticated` events."""
    errors: list[str] | None = Field(default=None, validation_alias="E")
    """Error messages for `error` events."""
    subscriptions: list[Subscription] | None = Field(default=None, validation_alias="s")
    """Subscription list confirmed by `subscribed` / `unsubscribed`."""
    channel: Channel | None = Field(default=None, validation_alias="c")
    """Source channel for events that carry market data."""
    balances: list[Balance] | None = Field(default=None, validation_alias="B")
    """Balances payload for `account_*` events."""
    market: str | None = Field(default=None, validation_alias="M")
    """Market id for market-scoped events."""
    asks: list[list[str]] | None = Field(default=None, validation_alias="a")
    """Order-book ask levels, each `[price, volume]` (string)."""
    bids: list[list[str]] | None = Field(default=None, validation_alias="b")
    """Order-book bid levels, each `[price, volume]` (string)."""
    first_update_id: int | None = Field(default=None, validation_alias="fi")
    """First update id covered by an order-book diff."""
    last_update_id: int | None = Field(default=None, validation_alias="li")
    """Last update id covered by an order-book diff."""
    version: int | None = Field(default=None, validation_alias="v")
    """Snapshot version counter for the book."""
    orders: list[Order] | None = Field(default=None, validation_alias="o")
    """Orders payload for `order_*` / `mwallet_order_*` events."""
    ticker: Ticker | None = Field(default=None, validation_alias="tk")
    """Ticker payload for `ticker` events."""
    trades: list[Trade] | None = Field(default=None, validation_alias="t")
    """Trade payload for `trade_*` events."""
    currency: str | None = Field(default=None, validation_alias="cu")
    """Currency code for currency-scoped events."""
    kline: KLine | None = Field(default=None, validation_alias="k")
    """Kline payload for `kline` events."""
    market_status: list[MarketStatus] | None = Field(default=None, validation_alias="ms")
    """Market status payload for `market_status` events."""
    pool_quota: PoolQuota | None = Field(default=None, validation_alias="qta")
    """Pool quota payload for `pool_quota` events."""
    m_wallet_ad_ratio: MWalletADRatio | None = Field(default=None, validation_alias="ad")
    """M-Wallet account-debt ratio payload."""
    m_wallet_borrowings: list[MWalletBorrowing] | None = Field(default=None, validation_alias="db")
    """M-Wallet borrowing payload for `borrowing_*` events."""

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)
