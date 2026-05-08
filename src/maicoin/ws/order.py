from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from enum import StrEnum
from typing import cast

from maicoin.ws.side import Side


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    POST_ONLY = "post_only"
    IOC_LIMIT = "ioc_limit"


class OrderState(StrEnum):
    CANCEL = "cancel"
    WAIT = "wait"
    DONE = "done"
    CONVERT = "convert"
    FINALIZING = "finalizing"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class Order:
    order_id: int
    side: Side
    order_type: OrderType
    price: str
    stop_price: str | None
    average_price: str
    state: OrderState
    market: str
    created_at: datetime
    updated_at: datetime | None
    volume: str
    remaining_volume: str
    executed_volume: str
    trade_count: int
    client_order_id: str | None
    group_id: int | None = None

    @classmethod
    def model_validate(cls, payload: object) -> Order:
        data = _expect_mapping(payload)
        return cls(
            order_id=_int(data["i"]),
            side=Side(data["sd"]),
            order_type=OrderType(data["ot"]),
            price=str(data["p"]),
            stop_price=_optional_str(data.get("sp")),
            average_price=str(data["ap"]),
            state=OrderState(data["S"]),
            market=str(data["M"]),
            created_at=_ms_datetime(data["T"]),
            updated_at=_optional_ms_datetime(data.get("TU")),
            volume=str(data["v"]),
            remaining_volume=str(data["rv"]),
            executed_volume=str(data["ev"]),
            trade_count=_int(data["tc"]),
            client_order_id=_optional_str(data.get("ci")),
            group_id=_optional_int(data.get("gi")),
        )


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _int(value: object) -> int:
    return int(cast("int | str | float", value))


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return _int(value)


def _ms_datetime(value: object) -> datetime:
    return datetime.fromtimestamp(_int(value) / 1000, tz=UTC)


def _optional_ms_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    return _ms_datetime(value)
