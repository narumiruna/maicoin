from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .side import Side


# https://maicoin.github.io/max-websocket-docs/#/private_channels?id=trade-response
class Trade(BaseModel):
    id: int | None = Field(default=None, validation_alias="i")
    market: str | None = Field(default=None, validation_alias="M")
    side: Side | None = Field(default=None, validation_alias="sd")
    price: float = Field(validation_alias="p")
    volume: float = Field(validation_alias="v")
    fee: float | None = Field(default=None, validation_alias="f")
    fee_currency: str | None = Field(default=None, validation_alias="fc")
    fee_discounted: bool | None = Field(default=None, validation_alias="fd")
    funds: str | None = Field(default=None, validation_alias="fn")
    created_at: datetime = Field(validation_alias="T")
    updated_at: datetime | None = Field(default=None, validation_alias="TU")
    maker: bool | None = Field(default=None, validation_alias="m")
    order_id: int | None = Field(default=None, validation_alias="oi")
    trend: str | None = Field(default=None, validation_alias="tr")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000)

    @field_validator("price", "volume", "fee", mode="before")
    @classmethod
    def convert_float(cls, s: str) -> float:
        return float(s)
