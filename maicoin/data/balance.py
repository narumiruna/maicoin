from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Balance:
    currency: float
    available: float
    locked: float

    @classmethod
    def from_dict(cls, d: dict) -> Balance:
        return cls(
            currency=d.get('cu'),
            available=d.get('av'),
            locked=d.get('l'),
        )
