from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import Literal
from typing import cast

RESOLUTION = Literal["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=field
@dataclass(slots=True, frozen=True)
class KLine:
    start_time: datetime
    end_time: datetime
    market: str
    resolution: RESOLUTION
    open: str
    high: str
    low: str
    close: str
    volume: str
    last_trade_id: int
    closed: bool

    @classmethod
    def model_validate(cls, payload: object) -> KLine:
        data = _expect_mapping(payload)
        return cls(
            start_time=_ms_datetime(data["ST"]),
            end_time=_ms_datetime(data["ET"]),
            market=str(data["M"]),
            resolution=cast("RESOLUTION", str(data["R"])),
            open=str(data["O"]),
            high=str(data["H"]),
            low=str(data["L"]),
            close=str(data["C"]),
            volume=str(data["v"]),
            last_trade_id=int(cast("int | str | float", data["ti"])),
            closed=_bool(data["x"]),
        )


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _ms_datetime(value: object) -> datetime:
    return datetime.fromtimestamp(int(cast("int | str | float", value)) / 1000, tz=UTC)


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    msg = f"expected bool, got {type(value).__name__}"
    raise TypeError(msg)
