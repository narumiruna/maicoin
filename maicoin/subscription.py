from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event


@dataclass
class Subscription:
    channel: Channel
    market: str
    depth: int = None

    def to_dict(self) -> dict:
        d = {
            'channel': self.channel.value,
            'market': self.market,
        }

        if self.depth is not None:
            d['depth'] = self.depth

        return d

    @classmethod
    def from_dict(self, d: dict) -> Subscription:
        return Subscription(
            channel=Channel(d.get('channel')),
            market=d.get('market'),
            depth=d.get('depth'),
        )


@dataclass
class SubscriptionAction:
    subscriptions: List[Subscription]

    def to_dict(self) -> dict:
        d = {
            'action': 'sub',
            'subscriptions': [s.to_dict() for s in self.subscriptions],
            'id': str(uuid.uuid4()),
        }
        return d


@dataclass
class SubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    created_at: int

    @classmethod
    def from_dict(cls, d: dict) -> SubscribedEvent:
        event = Event(d.get('e'))
        subscriptions = [Subscription.from_dict(s) for s in d.get('s')]
        id = d.get('i')
        created_at = d.get('T')

        return cls(event, subscriptions, id, created_at)


@dataclass
class UnsubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    created_at: int

    @classmethod
    def from_dict(cls, d: dict) -> UnsubscribedEvent:
        event = Event(d.get('e'))
        subscriptions = [Subscription.from_dict(s) for s in d.get('s')]
        id = d.get('i')
        created_at = d.get('T')

        return cls(event, subscriptions, id, created_at)
