from __future__ import annotations

from dataclasses import dataclass

from ..enums import Side

from ..enums import OrderState, OrderType


@dataclass
class Order:
    order_id: str
    side: Side
    order_type: OrderType
    price: str
    stop_price: str
    average_price: str
    state: OrderState
    market: str
    created_at: str
    volume: str
    remaining_volume: str
    executed_volume: str
    trade_count: int
    client_order_id: str
    group_id: str

    @classmethod
    def from_dict(cls, d: dict) -> Order:
        return cls(
            order_id=d.get('i'),
            side=Side(d.get('sd')),
            order_type=OrderType(d.get('ot')),
            price=d.get('p'),
            stop_price=d.get('sp'),
            average_price=d.get('ap'),
            state=OrderState(d.get('S')),
            market=d.get('M'),
            created_at=d.get('T'),
            volume=d.get('v'),
            remaining_volume=d.get('rv'),
            executed_volume=d.get('ev'),
            trade_count=d.get('tc'),
            client_order_id=d.get('ci'),
            group_id=d.get('gi'),
        )
