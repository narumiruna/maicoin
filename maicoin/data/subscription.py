from __future__ import annotations

from pydantic import BaseModel

from ..enums import Channel


class Subscription(BaseModel):
    channel: Channel
    market: str
    depth: int | None = None
