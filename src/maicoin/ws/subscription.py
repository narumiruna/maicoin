from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from maicoin.ws.channel import Channel


@dataclass(slots=True, frozen=True)
class Subscription:
    channel: Channel
    market: str | None = None
    depth: int | None = None
    resolution: str | None = None
    currency: str | None = None

    @classmethod
    def model_validate(cls, payload: Mapping[str, object]) -> Subscription:
        return cls(
            channel=Channel(payload["channel"]),
            market=_optional_str(payload.get("market")),
            depth=_optional_int(payload.get("depth")),
            resolution=_optional_str(payload.get("resolution")),
            currency=_optional_str(payload.get("currency")),
        )

    def model_dump(self, *, exclude_none: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "channel": self.channel,
            "market": self.market,
            "depth": self.depth,
            "resolution": self.resolution,
            "currency": self.currency,
        }
        if exclude_none:
            return {key: value for key, value in payload.items() if value is not None}
        return payload


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int | str | float):
        return int(value)
    msg = f"expected int-compatible value, got {type(value).__name__}"
    raise TypeError(msg)
