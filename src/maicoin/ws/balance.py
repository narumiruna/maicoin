from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import cast


@dataclass(slots=True, frozen=True)
class Balance:
    currency: str
    available: str
    locked: str
    staked: str | None = None
    balance_updated_time: datetime | None = None

    @classmethod
    def model_validate(cls, payload: object) -> Balance:
        data = _expect_mapping(payload)
        return cls(
            currency=str(data["cu"]),
            available=str(data["av"]),
            locked=str(data["l"]),
            staked=_optional_str(data.get("stk")),
            balance_updated_time=_optional_ms_datetime(data.get("TU")),
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


def _optional_ms_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(int(cast("int | str | float", value)) / 1000, tz=UTC)
