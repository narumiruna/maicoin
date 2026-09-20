from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import overload


@overload
def from_milliseconds(value: int) -> datetime: ...


@overload
def from_milliseconds(value: None) -> None: ...


def from_milliseconds(value: int | None) -> datetime | None:
    """Convert a MAX millisecond timestamp to an aware UTC datetime."""
    if value is None:
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=UTC)
