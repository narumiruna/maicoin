from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ticker:
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_dict(cls, d: dict) -> Ticker:
        return cls(
            open=d.get("O"),
            high=d.get("H"),
            low=d.get("L"),
            close=d.get("C"),
            volume=d.get("v"),
        )
