from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from ..enums import Side


class Trade(BaseModel):
    price: float = Field(validation_alias="p")
    volume: float = Field(validation_alias="v")
    created_at: datetime = Field(validation_alias="T")
    trend: str | None = Field(default=None, validation_alias="tr")
    id: str | int | None = Field(default=None, validation_alias="i")
    market: str | None = Field(default=None, validation_alias="M")
    side: Side | None = Field(default=None, validation_alias="sd")
    fee: float | None = Field(default=None, validation_alias="f")
    fee_currency: str | None = Field(default=None, validation_alias="fc")
    maker: bool | None = Field(default=None, validation_alias="m")

    @field_validator("created_at", mode="before")
    @classmethod
    def convert(cls, t: int) -> None:
        return datetime.fromtimestamp(int(t) / 1000)
