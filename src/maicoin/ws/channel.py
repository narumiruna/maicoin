"""Channel identifiers used in WebSocket subscriptions and responses."""

from enum import StrEnum


class Channel(StrEnum):
    """Public and private MAX WebSocket channels.

    See the [MAX WebSocket docs](https://maicoin.github.io/max-websocket-docs/)
    for the full event list emitted by each channel.
    """

    BOOK = "book"
    """Order-book snapshots and incremental updates for a market."""
    TRADE = "trade"
    """Public trade prints for a market."""
    TICKER = "ticker"
    """Rolling 24h ticker updates for a market."""
    USER = "user"
    """Private user channel: orders, trades, and account balances."""
    KLINE = "kline"
    """Candle stream at a configurable resolution."""
    MARKET_STATUS = "market_status"
    """Global market on/off and trading-mode changes."""
    POOL_QUOTA = "pool_quota"
    """M-Wallet borrow pool quotas, scoped by `currency`."""
