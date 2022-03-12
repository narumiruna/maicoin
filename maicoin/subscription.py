from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List


class Channel(Enum):
    BOOK = 'book'
    TRADE = 'trade'
    TICKER = 'ticker'
    USER = 'user'


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
    def parse(self, d: dict) -> Subscription:
        return Subscription(
            channel=Channel(d.get('channel')),
            market=d.get('market'),
            depth=d.get('depth'),
        )


@dataclass
class SubscriptionList:
    subscriptions: List[Subscription]

    def to_dict(self) -> dict:
        d = {
            'action': 'sub',
            'subscriptions': [s.to_dict() for s in self.subscriptions],
            'id': str(uuid.uuid4()),
        }
        return d
