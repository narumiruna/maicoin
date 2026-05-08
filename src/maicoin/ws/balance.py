from __future__ import annotations

from datetime import UTC
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class Balance(BaseModel):
    currency: str = Field(validation_alias="cu")
    available: str = Field(validation_alias="av")
    locked: str = Field(validation_alias="l")
    staked: str | None = Field(default=None, validation_alias="stk")
    balance_updated_time: datetime | None = Field(default=None, validation_alias="TU")

    @field_validator("balance_updated_time", mode="before")
    @classmethod
    def convert_datetime(cls, t: int | None) -> datetime | None:
        if t is None:
            return None
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)
