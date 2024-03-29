from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from ..enums import Channel
from ..enums import EventType
from .balance import Balance
from .order import Order
from .subscription import Subscription
from .ticker import Ticker
from .trade import Trade


class Event(BaseModel):
    event: EventType = Field(validation_alias="e")
    created_at: datetime = Field(validation_alias="T")
    id: str | None = Field(default=None, validation_alias="i")
    errors: list[str] | None = Field(default=None, validation_alias="E")
    subscriptions: list[Subscription] | None = Field(default=None, validation_alias="s")
    channel: Channel | None = Field(default=None, validation_alias="c")
    balances: list[Balance] | None = Field(default=None, validation_alias="B")
    market: str = Field(default="", validation_alias="M")
    asks: list[list[float]] | None = Field(default=None, validation_alias="a")
    bids: list[list[float]] | None = Field(default=None, validation_alias="b")
    orders: list[Order] | None = Field(default=None, validation_alias="o")
    ticker: Ticker | None = Field(default=None, validation_alias="tk")
    trades: list[Trade] | None = Field(default=None, validation_alias="t")
    currency: str | None = Field(default=None, validation_alias="cu")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> None:
        return datetime.fromtimestamp(int(t) / 1000)
