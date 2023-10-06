from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..enums import Side
from ..utils import to_datetime


@dataclass
class Trade:
    price: float
    volume: float
    created_at: datetime
    trend: str
    id: str = None
    market: str = None
    side: Side = None
    fee: float = None
    fee_currency: str = None
    maker: bool = None

    def __post_init__(self):
        self.created_at = to_datetime(self.created_at)

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        return cls(
            price=d.get("p"),
            volume=d.get("v"),
            created_at=d.get("T"),
            trend=d.get("tr"),
            id=d.get("i"),
            market=d.get("M"),
            side=d.get("sd"),
            fee=d.get("f"),
            fee_currency=d.get("fc"),
            maker=d.get("m"),
        )
