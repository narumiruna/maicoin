from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event
from .side import Side

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


# {
#   "c": "user",
#   "e": "trade_snapshot",
#   "t": [{
#     "i": 68444, // trade id
#     "p": "21499.0",
#     "v": "0.2658",
#     "M": "ethtwd",
#     "T": 1521726960357,
#     "sd": "bid",
#     "f": "3.2",
#     "fc": "twd",
#     "m": true    // maker
#   }],
#   "T": 1521726960357
# }
@dataclass
class Trade:
    price: float
    volume: float
    created_at: str
    trend: str
    id: str = None
    market: str = None
    side: Side = None
    fee: float = None
    fee_currency: str = None
    maker: bool = None

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        return cls(
            d.get('p'),
            d.get('v'),
            d.get('T'),
            d.get('tr'),
            id=d.get('i'),
            market=d.get('M'),
            side=d.get('sd'),
            fee=d.get('f'),
            fee_currency=d.get('fc'),
            maker=d.get('m'),
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
            [Trade.from_dict(trade) for trade in d.get('t')],
            d.get('T'),
        )
