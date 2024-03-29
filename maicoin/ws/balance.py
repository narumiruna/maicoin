from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class Balance(BaseModel):
    currency: str = Field(validation_alias="cu")
    available: float = Field(validation_alias="av")
    locked: float = Field(validation_alias="l")
    staked: str | float | None = Field(default=None, validation_alias="stk")
    balance_updated_time: datetime = Field(validation_alias="TU")

    @field_validator("balance_updated_time", mode="before")
    @classmethod
    def convert(cls, t: int) -> None:
        return datetime.fromtimestamp(int(t) / 1000)
