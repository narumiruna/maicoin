from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import cast

from maicoin.ws.side import Side


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=trade-response
@dataclass(slots=True, frozen=True)
class Trade:
    id: int | None
    market: str | None
    side: Side | None
    price: str
    volume: str
    fee: str | None = None
    fee_currency: str | None = None
    fee_discounted: bool | None = None
    funds: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    maker: bool | None = None
    order_id: int | None = None
    trend: str | None = None

    @classmethod
    def model_validate(cls, payload: object) -> Trade:
        data = _expect_mapping(payload)
        return cls(
            id=_optional_int(data.get("i")),
            market=_optional_str(data.get("M")),
            side=None if data.get("sd") is None else Side(data["sd"]),
            price=str(data["p"]),
            volume=str(data["v"]),
            fee=_optional_str(data.get("f")),
            fee_currency=_optional_str(data.get("fc")),
            fee_discounted=_optional_bool(data.get("fd")),
            funds=_optional_str(data.get("fn")),
            created_at=_optional_ms_datetime(data.get("T")),
            updated_at=_optional_ms_datetime(data.get("TU")),
            maker=_optional_bool(data.get("m")),
            order_id=_optional_int(data.get("oi")),
            trend=_optional_str(data.get("tr")),
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


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(cast("int | str | float", value))


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    msg = f"expected bool, got {type(value).__name__}"
    raise TypeError(msg)


def _optional_ms_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(int(cast("int | str | float", value)) / 1000, tz=UTC)
