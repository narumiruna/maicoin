from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event


@dataclass
class PriceVolume:
    price: float
    volume: float


# {
#  "c": "book",
#  "e": "snapshot",
#  "M": "btcusdt",
#  "a": [["5337.3", "0.1"]],
#  "b": [["5333.3", "0.5"]],
#  "T": 1591869939634
# }
@dataclass
class BookEvent:
    channel: Channel
    event: Event
    market: str
    asks: List[PriceVolume]
    bids: List[PriceVolume]
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> BookEvent:
        return cls(
            Channel(d.get('c')),
            Event(d.get('e')),
            d.get('M'),
            [PriceVolume(p, v) for p, v in d.get('a')],
            [PriceVolume(p, v) for p, v in d.get('b')],
            d.get('T'),
        )
