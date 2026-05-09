"""Subscription model used by `sub` / `unsub` requests."""

from __future__ import annotations

from pydantic import BaseModel

from maicoin.ws.channel import Channel


class Subscription(BaseModel):
    """A single channel subscription.

    Field semantics depend on `channel`:

    - Public channels (`book`, `trade`, `ticker`, `kline`) require `market`.
    - `book` accepts a `depth` (1, 5, 10, 20, 50).
    - `kline` accepts a `resolution` (e.g. `"1m"`, `"5m"`).
    - Private channels (`user`) are tied to the authenticated session and
      ignore `market` / `depth` / `resolution`.
    - `pool_quota` accepts `currency` for M-Wallet pool tracking.
    - `market_status` is global and needs no extra fields.
    """

    channel: Channel
    """The channel to subscribe to."""
    market: str | None = None
    """Market id (e.g. `"btcusdt"`) for market-scoped channels."""
    depth: int | None = None
    """Order-book depth for `book`. Allowed values: 1, 5, 10, 20, 50."""
    resolution: str | None = None
    """Candle resolution for `kline` (e.g. `"1m"`, `"15m"`, `"1h"`)."""
    currency: str | None = None
    """Currency code for currency-scoped channels such as `pool_quota`."""
