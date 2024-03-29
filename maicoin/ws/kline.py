from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

RESOLUTION = Literal["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=field
class KLine(BaseModel):
    start_time: datetime = Field(validation_alias="ST")
    end_time: datetime = Field(validation_alias="ET")
    market: str = Field(validation_alias="M")
    resolution: RESOLUTION = Field(validation_alias="R")
    open: float = Field(validation_alias="O")
    high: float = Field(validation_alias="H")
    low: float = Field(validation_alias="L")
    close: float = Field(validation_alias="C")
    volume: float = Field(validation_alias="v")
    last_trade_id: int = Field(validation_alias="ti")
    closed: bool = Field(validation_alias="x")

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000)

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def convert_float(cls, s: str) -> float:
        return float(s)
