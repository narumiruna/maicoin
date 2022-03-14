from __future__ import annotations

from dataclasses import dataclass

from .channel import Channel
from .event import Event

# {
#  "c": "ticker",
#  "e": "snapshot",
#  "M": "btctwd",
#  "tk": {
#     "O": "280007.1",
#     "H": "280017.2",
#     "L": "280005.3",
#     "C": "280004.5",
#     "v": "71.01"
#  },
#  "T": 123456789
# }

# {
#  "c": "ticker",
#  "e": "update",
#  "M": "btctwd",
#  "tk": {
#     "O": "280007.1",
#     "H": "280017.2",
#     "L": "280005.3",
#     "C": "280004.5",
#     "v": "71.01"
#  },
#  "T": 123456789
# }


@dataclass
class Ticker:
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_dict(cls, d: dict) -> Ticker:
        return cls(
            d.get('O'),
            d.get('H'),
            d.get('L'),
            d.get('C'),
            d.get('v'),
        )


@dataclass
class TickerEvent:
    channel: Channel
    event: Event
    market: str
    ticker: Ticker
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> TickerEvent:
        return cls(
            d.get('c'),
            d.get('e'),
            d.get('M'),
            Ticker.from_dict(d.get('tk')),
            d.get('T'),
        )
