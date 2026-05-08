from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import cast


@dataclass(slots=True, frozen=True)
class PoolQuota:
    currency: str
    available: str
    updated_at: datetime

    @classmethod
    def model_validate(cls, payload: object) -> PoolQuota:
        data = _expect_mapping(payload)
        return cls(currency=str(data["cu"]), available=str(data["av"]), updated_at=_ms_datetime(data["TU"]))


@dataclass(slots=True, frozen=True)
class MWalletIndexPrice:
    market: str
    price: str

    @classmethod
    def model_validate(cls, payload: object) -> MWalletIndexPrice:
        data = _expect_mapping(payload)
        return cls(market=str(data["M"]), price=str(data["p"]))


@dataclass(slots=True, frozen=True)
class MWalletADRatio:
    ad_ratio: str
    asset_in_usdt: str
    debt_in_usdt: str
    index_prices: list[MWalletIndexPrice]
    updated_at: datetime

    @classmethod
    def model_validate(cls, payload: object) -> MWalletADRatio:
        data = _expect_mapping(payload)
        index_prices = data["idxp"]
        if not isinstance(index_prices, list):
            msg = f"expected index_prices list, got {type(index_prices).__name__}"
            raise TypeError(msg)
        return cls(
            ad_ratio=str(data["ad"]),
            asset_in_usdt=str(data["as"]),
            debt_in_usdt=str(data["db"]),
            index_prices=[MWalletIndexPrice.model_validate(item) for item in index_prices],
            updated_at=_ms_datetime(data["TU"]),
        )


@dataclass(slots=True, frozen=True)
class MWalletBorrowing:
    currency: str
    debt_principal: str
    debt_interest: str
    updated_at: datetime

    @classmethod
    def model_validate(cls, payload: object) -> MWalletBorrowing:
        data = _expect_mapping(payload)
        return cls(
            currency=str(data["cu"]),
            debt_principal=str(data["dbp"]),
            debt_interest=str(data["dbi"]),
            updated_at=_ms_datetime(data["TU"]),
        )


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _ms_datetime(value: object) -> datetime:
    return datetime.fromtimestamp(int(cast("int | str | float", value)) / 1000, tz=UTC)
