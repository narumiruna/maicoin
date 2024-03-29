from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from ..enums import OrderState
from ..enums import OrderType
from ..enums import Side


class Order(BaseModel):
    order_id: str = Field(validation_alias="i")
    side: Side = Field(validation_alias="sd")
    order_type: OrderType = Field(validation_alias="ot")
    price: str = Field(validation_alias="p")
    stop_price: str = Field(validation_alias="sp")
    average_price: str = Field(validation_alias="ap")
    state: OrderState = Field(validation_alias="S")
    market: str = Field(validation_alias="M")
    created_at: int = Field(validation_alias="T")
    volume: str = Field(validation_alias="v")
    remaining_volume: str = Field(validation_alias="rv")
    executed_volume: str = Field(validation_alias="ev")
    trade_count: int = Field(validation_alias="tc")
    client_order_id: str = Field(validation_alias="ci")
    group_id: str = Field(validation_alias="gi")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> None:
        return datetime.fromtimestamp(int(t) / 1000)
