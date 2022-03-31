from __future__ import annotations

from dataclasses import dataclass

from ..enums import Channel


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
