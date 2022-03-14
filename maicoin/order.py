from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from .channel import Channel
from .event import Event
from .side import Side


class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP_MARKET = 'stop_market'
    STOP_LIMIT = 'stop_limit'
    POST_ONLY = 'post_only'
    IOC_LIMIT = 'ioc_limit'


class OrderState(Enum):
    CANCEL = 'cancel'
    WAIT = 'wait'
    DONE = 'done'
    CONVERT = 'convert'
    FINALIZING = 'finalizing'
    FAILED = 'failed'


# {
#   "c": "user",
#   "e": "order_snapshot",
#   "o": [{
#      "i": 87, // order id
#      "sd": "bid",
#      "ot": "limit",
#      "p": "21499.0",
#      "sp": "21499.0",
#      "ap": "21499.0",
#      "S": "done",
#      "M": "ethtwd",
#      "T": 1521726960123,
#      "v": "0.2658",
#      "rv": "0.0",
#      "ev": "0.2658",
#      "tc": 1,
#      "ci": "client-oid-1",
#      "gi": 123 // group id
#   }, ...],
#   "T": 1521726960357
# }


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
            d.get('i'),
            Side(d.get('sd')),
            OrderType(d.get('ot')),
            d.get('p'),
            d.get('sp'),
            d.get('ap'),
            OrderState(d.get('S')),
            d.get('M'),
            d.get('T'),
            d.get('v'),
            d.get('rv'),
            d.get('ev'),
            d.get('tc'),
            d.get('ci'),
            d.get('gi'),
        )


@dataclass
class OrderEvent:
    channel: Channel
    event: Event
    order: List[Order]
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> OrderEvent:
        return cls(
            Channel(d.get('c')),
            Event(d.get('e')),
            [Order.from_dict(order) for order in d.get('o')],
            d.get('T'),
        )
