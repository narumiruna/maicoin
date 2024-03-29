from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


# https://maicoin.github.io/max-websocket-docs/#/public_ticker?id=success-response
class Ticker(BaseModel):
    market: str = Field(validation_alias="M")
    open: float = Field(validation_alias="O")
    high: float = Field(validation_alias="H")
    low: float = Field(validation_alias="L")
    close: float = Field(validation_alias="C")
    volume: float = Field(validation_alias="v")
    volume_in_btc: float = Field(validation_alias="V")

    @field_validator("open", "high", "low", "close", "volume", "volume_in_btc", mode="before")
    @classmethod
    def convert_float(cls, s: str) -> float:
        return float(s)
