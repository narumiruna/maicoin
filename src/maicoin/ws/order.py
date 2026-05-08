from __future__ import annotations

from datetime import UTC
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from maicoin.ws.side import Side


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    POST_ONLY = "post_only"
    IOC_LIMIT = "ioc_limit"


class OrderState(StrEnum):
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
    price: str = Field(validation_alias="p")
    stop_price: str | None = Field(default=None, validation_alias="sp")
    average_price: str = Field(validation_alias="ap")
    state: OrderState = Field(validation_alias="S")
    market: str = Field(validation_alias="M")
    created_at: datetime = Field(validation_alias="T")
    updated_at: datetime | None = Field(default=None, validation_alias="TU")
    volume: str = Field(validation_alias="v")
    remaining_volume: str = Field(validation_alias="rv")
    executed_volume: str = Field(validation_alias="ev")
    trade_count: int = Field(validation_alias="tc")
    client_order_id: str | None = Field(validation_alias="ci")
    group_id: int | None = Field(default=None, validation_alias="gi")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int | None) -> datetime | None:
        if t is None:
            return None
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)
