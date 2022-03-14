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
            Channel(d.get('channel')),
            d.get('market'),
            d.get('depth'),
        )


@dataclass
class SubscriptionAction:
    subscriptions: List[Subscription]

    def to_dict(self) -> dict:
        return {
            'action': 'sub',
            'subscriptions': [s.to_dict() for s in self.subscriptions],
            'id': str(uuid.uuid4()),
        }


@dataclass
class SubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> SubscribedEvent:
        return cls(
            Event(d.get('e')),
            [Subscription.from_dict(s) for s in d.get('s')],
            d.get('i'),
            d.get('T'),
        )


@dataclass
class UnsubscribedEvent:
    event: Event
    subscriptions: List[Subscription]
    id: str
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> UnsubscribedEvent:
        return cls(
            Event(d.get('e')),
            [Subscription.from_dict(s) for s in d.get('s')],
            d.get('i'),
            d.get('T'),
        )
