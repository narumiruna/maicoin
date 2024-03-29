from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class Ticker(BaseModel):
    market: str = Field(validation_alias="M")
    open: str | float = Field(validation_alias="O")
    high: str | float = Field(validation_alias="H")
    low: str | float = Field(validation_alias="L")
    close: str | float = Field(validation_alias="C")
    volume: str | float = Field(validation_alias="v")
    volume_in_btc: str | float = Field(validation_alias="V")
