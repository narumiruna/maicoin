from __future__ import annotations

from pydantic import BaseModel

from .channel import Channel


class Subscription(BaseModel):
    channel: Channel
    market: str | None = None
    depth: int | None = None
    resolution: str | None = None
