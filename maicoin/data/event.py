from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..enums import Channel
from ..enums import EventType
from .balance import Balance
from .order import Order
from .subscription import Subscription
from .ticker import Ticker
from .trade import Trade


@dataclass
class Event:
    event: EventType
    created_at: str
    id: str = None
    errors: List[str] = None
    subscriptions: List[Subscription] = None
    channel: Channel = None
    balances: List[Balance] = None
    market: str = None
    asks: List[List[float]] = None
    bids: List[List[float]] = None
    orders: List[Order] = None
    ticker: Ticker = None
    trades: List[Trade] = None

    @classmethod
    def from_dict(cls, d: dict) -> Event:
        d = dict(
            event=EventType(d.get('e')),
            created_at=d.get('T'),
            id=d.get('i'),
            errors=d.get('E'),
            market=d.get('M'),
            asks=d.get('a'),
            bids=d.get('b'),
        )

        channel = d.get('c')
        if channel:
            d['channel'] = Channel(channel)

        subscriptions = d.get('s')
        if subscriptions:
            d['subscriptions'] = [Subscription.from_dict(s) for s in subscriptions]

        balances = d.get('B')
        if balances:
            d['balances'] = [Balance.from_dict(balance) for balance in balances]

        orders = d.get('o')
        if orders:
            d['orders'] = [Order.from_dict(order) for order in orders]

        ticker = d.get('tk')
        if ticker:
            d['ticker'] = Ticker.from_dict(ticker)

        trades = d.get('t')
        if trades:
            d['trades'] = [Trade.from_dict(trade) for trade in trades]

        d = {k: v for k, v in d.items() if v is not None}

        return cls(**d)
