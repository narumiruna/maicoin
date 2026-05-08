from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast


# https://maicoin.github.io/max-websocket-docs/#/public_ticker?id=success-response
@dataclass(slots=True, frozen=True)
class Ticker:
    market: str
    open: str
    high: str
    low: str
    close: str
    volume: str
    volume_in_btc: str

    @classmethod
    def model_validate(cls, payload: object) -> Ticker:
        data = _expect_mapping(payload)
        return cls(
            market=str(data["M"]),
            open=str(data["O"]),
            high=str(data["H"]),
            low=str(data["L"]),
            close=str(data["C"]),
            volume=str(data["v"]),
            volume_in_btc=str(data["V"]),
        )


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)
