from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .side import Side


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    POST_ONLY = "post_only"
    IOC_LIMIT = "ioc_limit"


class OrderState(str, Enum):
    CANCEL = "cancel"
    WAIT = "wait"
    DONE = "done"
    CONVERT = "convert"
    FINALIZING = "finalizing"
    FAILED = "failed"


class Order(BaseModel):
    order_id: int = Field(validation_alias="i")
    side: Side = Field(validation_alias="sd")
    order_type: OrderType = Field(validation_alias="ot")
    price: float = Field(validation_alias="p")
    stop_price: float | None = Field(default=None, validation_alias="sp")
    average_price: float = Field(validation_alias="ap")
    state: OrderState = Field(validation_alias="S")
    market: str = Field(validation_alias="M")
    created_at: datetime = Field(validation_alias="T")
    volume: float = Field(validation_alias="v")
    remaining_volume: float = Field(validation_alias="rv")
    executed_volume: float = Field(validation_alias="ev")
    trade_count: int = Field(validation_alias="tc")
    client_order_id: str = Field(validation_alias="ci")
    group_id: int | None = Field(default=None, validation_alias="gi")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000)

    @field_validator(
        "price", "average_price", "stop_price", "volume", "remaining_volume", "executed_volume", mode="before"
    )
    @classmethod
    def convert_float(cls, s: str) -> float:
        return float(s)
