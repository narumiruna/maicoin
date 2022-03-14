from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event

# {
#   "c": "trade",
#   "e": "snapshot",
#   "M": "btctwd",
#   "t":[{
#     "p": "5337.3",
#     "v": "0.1",
#     "T": 123456789,
#     "tr": "up"
#   }],
#   "T": 123456789
# }


@dataclass
class Trade:
    price: float
    volume: float
    created_at: int
    trend: str

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        price = d.get('p')
        volume = d.get('v')
        created_at = d.get('T')
        trend = d.get('tr')
        return cls(price, volume, created_at, trend)


@dataclass
class TradeEvent:
    channel: Channel
    event: Event
    market: str
    trades: List[Trade]
    created_at: int

    @classmethod
    def from_dict(cls, d: dict) -> TradeEvent:
        channel = Channel(d.get('c'))
        event = Event(d.get('e'))
        market = d.get('M')
        trades = [Trade.from_dict(t) for t in d.get('t')]
        created_at = d.get('T')
        return cls(channel, event, market, trades, created_at)
