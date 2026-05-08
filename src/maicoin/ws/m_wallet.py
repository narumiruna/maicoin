from __future__ import annotations

from datetime import UTC
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class PoolQuota(BaseModel):
    currency: str = Field(validation_alias="cu")
    available: str = Field(validation_alias="av")
    updated_at: datetime = Field(validation_alias="TU")

    @field_validator("updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)


class MWalletIndexPrice(BaseModel):
    market: str = Field(validation_alias="M")
    price: str = Field(validation_alias="p")


class MWalletADRatio(BaseModel):
    ad_ratio: str = Field(validation_alias="ad")
    asset_in_usdt: str = Field(validation_alias="as")
    debt_in_usdt: str = Field(validation_alias="db")
    index_prices: list[MWalletIndexPrice] = Field(validation_alias="idxp")
    updated_at: datetime = Field(validation_alias="TU")

    @field_validator("updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)


class MWalletBorrowing(BaseModel):
    currency: str = Field(validation_alias="cu")
    debt_principal: str = Field(validation_alias="dbp")
    debt_interest: str = Field(validation_alias="dbi")
    updated_at: datetime = Field(validation_alias="TU")

    @field_validator("updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, t: int) -> datetime:
        return datetime.fromtimestamp(int(t) / 1000, tz=UTC)
