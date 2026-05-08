from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import cast


class Status(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCEL_ONLY = "cancel-only"


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=field
@dataclass(slots=True, frozen=True)
class MarketStatus:
    market: str
    status: Status
    base_unit: str
    base_unit_precision: int
    minimal_base_amount: float
    quote_unit: str
    quote_unit_precision: int
    minimal_quote_amount: float
    mwallet_supported: bool

    @classmethod
    def model_validate(cls, payload: object) -> MarketStatus:
        data = _expect_mapping(payload)
        return cls(
            market=str(data["M"]),
            status=Status(data["st"]),
            base_unit=str(data["bu"]),
            base_unit_precision=int(cast("int | str | float", data["bup"])),
            minimal_base_amount=float(cast("int | str | float", data["mba"])),
            quote_unit=str(data["qu"]),
            quote_unit_precision=int(cast("int | str | float", data["qup"])),
            minimal_quote_amount=float(cast("int | str | float", data["mqa"])),
            mwallet_supported=_bool(data["mws"]),
        )


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    msg = f"expected bool, got {type(value).__name__}"
    raise TypeError(msg)
