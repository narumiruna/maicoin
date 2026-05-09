from __future__ import annotations

from maicoin.v3.models.base import MaxBaseModel


class HistoricalIndexPrice(MaxBaseModel):
    timestamp: str
    price: str


class InterestRate(MaxBaseModel):
    hourly_interest_rate: str
    next_hourly_interest_rate: str


class MWalletLoan(MaxBaseModel):
    sn: str
    currency: str
    amount: str
    state: str
    created_at: int
    interest_rate: str


class MWalletTransfer(MaxBaseModel):
    sn: str
    side: str
    currency: str
    amount: str
    created_at: int
    state: str


class MWalletRepayment(MaxBaseModel):
    currency: str
    amount: str
    principal: str
    interest: str
    state: str
    sn: str
    created_at: int


class MWalletLiquidation(MaxBaseModel):
    sn: str
    ad_ratio: str
    expected_ad_ratio: str
    created_at: int
    state: str


class MWalletLiquidationRepayment(MaxBaseModel):
    currency: str
    amount: str
    principal: str
    interest: str
    state: str


class MWalletForcedLiquidation(MaxBaseModel):
    market: str
    type: str
    price: str
    volume: str
    fee: str
    fee_currency: str
    repayment: MWalletLiquidationRepayment


class MWalletLiquidationDetail(MWalletLiquidation):
    repayments: list[MWalletLiquidationRepayment]
    liquidations: list[MWalletForcedLiquidation]


class MWalletInterest(MaxBaseModel):
    currency: str
    amount: str
    interest_rate: str
    principal: str
    created_at: int


class MWalletADRatio(MaxBaseModel):
    ad_ratio: str
    asset_in_usdt: str
    debt_in_usdt: str
