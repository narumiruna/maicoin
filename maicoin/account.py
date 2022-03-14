from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .channel import Channel
from .event import Event

# {
#   "c": "user",
#   "e": "account_snapshot",
#   "B": [
#     {
#       "cu": "btc",
#       "av": "123.4",
#       "l": "0.5"
#     },
#     ...
#   ],
#   "T": 123456789
# }

# {
#   "c": "user",
#   "e": "account_update",
#   "B": [
#     {
#       "cu": "btc",
#       "av": "123.4",
#       "l": "0.5"
#     },
#     ...
#   ],
#   "T": 123456789,
# }


@dataclass
class Balance:
    currency: float
    available: float
    locked: float

    @classmethod
    def from_dict(cls, d: dict) -> Balance:
        return cls(
            d.get('cu'),
            d.get('av'),
            d.get('l'),
        )


@dataclass
class AccountEvent:
    channel: Channel
    event: Event
    balances: List[Balance]
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> AccountEvent:
        return cls(
            Channel(d.get('c')),
            Event(d.get('e')),
            [Balance.from_dict(balance) for balance in d.get('B')],
            d.get('T'),
        )
