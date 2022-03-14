from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event


@dataclass
class PriceVolume:
    price: float
    volume: float

    @classmethod
    def from_dict(cls, asks_or_bids: list) -> List[PriceVolume]:
        return [PriceVolume(p, v) for p, v in asks_or_bids]


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
    created_at: int

    @classmethod
    def from_dict(cls, d: dict) -> BookEvent:
        channel = Channel(d.get('c'))
        event = Event(d.get('e'))
        market = d.get('M')
        asks = PriceVolume.from_dict(d.get('a'))
        bids = PriceVolume.from_dict(d.get('b'))
        created_at = d.get('T')
        return cls(channel, event, market, asks, bids, created_at)
