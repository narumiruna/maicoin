from __future__ import annotations

from pydantic import Field

from maicoin.v3.models.base import MaxBaseModel


class Withdrawal(MaxBaseModel):
    uuid: str
    currency: str
    network_protocol: str | None
    amount: str
    fee: str
    fee_currency: str
    to_address: str
    label: str
    txid: str | None
    created_at: int
    state: str
    transaction_type: str


class WithdrawAddress(MaxBaseModel):
    uuid: str
    currency: str
    network_protocol: str | None
    address: str
    extra_label: str
    created_at: int
    activated_at: int | None
    is_internal: bool
    network_congested: bool


class Deposit(MaxBaseModel):
    uuid: str
    currency: str
    network_protocol: str
    amount: str
    to_address: str
    txid: str
    created_at: int
    confirmations: int
    state: str
    state_reason: str


class DepositAddress(MaxBaseModel):
    currency: str
    network_protocol: str
    currency_version: str
    address: str | None


class InternalTransfer(MaxBaseModel):
    uuid: str
    currency: str
    amount: str
    created_at: int
    from_: str = Field(validation_alias="from", serialization_alias="from")
    to: str
    state: str


class Reward(MaxBaseModel):
    uuid: str
    currency: str
    amount: str
    created_at: int
    type: str
    note: str


class FundTransactionDeposit(MaxBaseModel):
    sn: str
    is_internal: bool
    currency: str
    amount: str
    state: str
    created_at: int
    network_protocol: str | None
    to_address: str | None
    txid: str | None
    from_: str | None = Field(validation_alias="from", serialization_alias="from")


class FundTransactionWithdrawal(MaxBaseModel):
    sn: str
    is_internal: bool
    currency: str
    amount: str
    state: str
    created_at: int
    network_protocol: str | None
    fee: str | None
    fee_currency: str | None
    to_address: str | None
    label: str | None
    txid: str | None
    to: str | None


class FundTransactionSource(MaxBaseModel):
    platform: str
    sn: object
    wallet_type: str


class FundTransactionTransfer(MaxBaseModel):
    sn: str
    currency: str
    amount: str
    state: str
    created_at: int
    from_: FundTransactionSource = Field(validation_alias="from", serialization_alias="from")
    to: FundTransactionSource
