from __future__ import annotations

from pydantic import BaseModel

from .channel import Channel


class Subscription(BaseModel):
    channel: Channel
    market: str
    depth: int | None = None
