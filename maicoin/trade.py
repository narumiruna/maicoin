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
    created_at: str
    trend: str

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        return cls(
            d.get('p'),
            d.get('v'),
            d.get('T'),
            d.get('tr'),
        )


@dataclass
class TradeEvent:
    channel: Channel
    event: Event
    market: str
    trades: List[Trade]
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> TradeEvent:
        return cls(
            Channel(d.get('c')),
            Event(d.get('e')),
            d.get('M'),
            [Trade.from_dict(t) for t in d.get('t')],
            d.get('T'),
        )
