from enum import Enum

from pydantic import BaseModel
from pydantic import Field


class Status(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCEL_ONLY = "cancel-only"


# https://maicoin.github.io/max-websocket-docs/#/public_kline?id=field
class MarketStatus(BaseModel):
    market: str = Field(validation_alias="M")
    status: Status = Field(validation_alias="st")
    base_unit: str = Field(validation_alias="bu")
    base_unit_precision: int = Field(validation_alias="bup")
    minimal_base_amount: float = Field(validation_alias="mba")
    quote_unit: str = Field(validation_alias="qu")
    quote_unit_precision: int = Field(validation_alias="qup")
    minimal_quote_amount: float = Field(validation_alias="mqa")
    mwallet_supported: bool = Field(validation_alias="mws")
