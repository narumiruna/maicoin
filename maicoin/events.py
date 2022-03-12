from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import Channel
from . import Subscription

from enum import Enum


class Event(Enum):
    AUTHENTICATED = 'authenticated'
    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBED = 'unsubscribed'
    SNAPSHOT = 'snapshot'
    ORDER_SNAPSHOT = 'order_snapshot'
    TRADE_SNAPSHOT = 'trade_snapshot'
    ACCOUNT_SNAPSHOT = 'account_snapshot'
    ERROR = 'error'
    UPDATE = 'update'


@dataclass
class AuthenticatedEvent:
    event: Event
    id: str
    at: int

    @classmethod
    def parse(cls, d: dict) -> AuthenticatedEvent:
        event = Event(d.get('e'))
        id = d.get('i')
        at = d.get('T')

        return cls(event, id, at)


@dataclass
class SubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    at: str

    @classmethod
    def parse(cls, d: dict) -> SubscribedEvent:
        event = Event(d.get('e'))
        subscriptions = [Subscription.parse(s) for s in d.get('s')]
        id = d.get('i')
        at = d.get('T')

        return cls(event, subscriptions, id, at)


@dataclass
class UnsubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    at: str

    @classmethod
    def parse(cls, d: dict) -> UnsubscribedEvent:
        event = Event(d.get('e'))
        subscriptions = [Subscription.parse(s) for s in d.get('s')]
        id = d.get('i')
        at = d.get('T')

        return cls(event, subscriptions, id, at)


@dataclass
class PriceVolume:
    price: float
    volume: float

    @classmethod
    def parse(cls, asks_or_bids: list) -> List[PriceVolume]:
        return [PriceVolume(float(p), float(v)) for p, v in asks_or_bids]


# {
#  "c": "book",
#  "e": "snapshot",
#  "M": "btcusdt",
#  "a": [["5337.3", "0.1"]],
#  "b": [["5333.3", "0.5"]],
#  "T": 1591869939634
# }
@dataclass
class BookSnapshot:
    channel: Channel
    event: Event
    market: str
    asks: List[PriceVolume]
    bids: List[PriceVolume]
    at: str

    @classmethod
    def parse(cls, d: dict) -> BookSnapshot:
        channel = Channel(d.get('c'))
        event = Event(d.get('e'))
        market = d.get('M')
        asks = PriceVolume.parse(d.get('a'))
        bids = PriceVolume.parse(d.get('b'))
        at = d.get('T')

        return cls(channel, event, market, asks, bids, at)


def parse_snapshot(d: dict):
    channel = Channel(d.get('c'))

    if channel == Channel.BOOK:
        return BookSnapshot.parse(d)
    elif channel == Channel.TICKER:
        pass


def parse_response(d: dict):
    event = Event(d.get('e'))
    if event == Event.AUTHENTICATED:
        return AuthenticatedEvent.parse(d)
    elif event == Event.SUBSCRIBED:
        return SubscribedEvent.parse(d)
    elif event == Event.SUBSCRIBED:
        return UnsubscribedEvent.parse(d)
    elif event == event.SNAPSHOT:
        return parse_snapshot(d)
