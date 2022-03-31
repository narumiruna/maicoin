from __future__ import annotations

from dataclasses import dataclass

from ..enums import Side


@dataclass
class Trade:
    price: float
    volume: float
    created_at: str
    trend: str
    id: str = None
    market: str = None
    side: Side = None
    fee: float = None
    fee_currency: str = None
    maker: bool = None

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        return cls(
            price=d.get('p'),
            volume=d.get('v'),
            created_at=d.get('T'),
            trend=d.get('tr'),
            id=d.get('i'),
            market=d.get('M'),
            side=d.get('sd'),
            fee=d.get('f'),
            fee_currency=d.get('fc'),
            maker=d.get('m'),
        )
