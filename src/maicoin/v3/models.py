from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from pydantic import BaseModel
from pydantic import ConfigDict


class MaxBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _required_str(payload: Mapping[str, object], key: str) -> str:
    return str(payload[key])


def _required_int(payload: Mapping[str, object], key: str) -> int:
    value = payload[key]
    if isinstance(value, int | str | float):
        return int(value)
    msg = f"expected int-compatible {key}, got {type(value).__name__}"
    raise TypeError(msg)


def _optional_int(payload: Mapping[str, object], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, int | str | float):
        return int(value)
    msg = f"expected int-compatible {key}, got {type(value).__name__}"
    raise TypeError(msg)


def _optional_str(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    return str(value)


def _optional_bool(payload: Mapping[str, object], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    msg = f"expected bool {key}, got {type(value).__name__}"
    raise TypeError(msg)


def _required_float(payload: Mapping[str, object], key: str) -> float:
    value = payload[key]
    if isinstance(value, int | str | float):
        return float(value)
    msg = f"expected float-compatible {key}, got {type(value).__name__}"
    raise TypeError(msg)


def _required_bool(payload: Mapping[str, object], key: str) -> bool:
    value = payload[key]
    if isinstance(value, bool):
        return value
    msg = f"expected bool {key}, got {type(value).__name__}"
    raise TypeError(msg)


def _price_levels(value: object) -> list[tuple[str, str]]:
    if not isinstance(value, list):
        msg = f"expected price levels list, got {type(value).__name__}"
        raise TypeError(msg)
    levels: list[tuple[str, str]] = []
    for level in value:
        if not isinstance(level, list | tuple) or len(level) != 2:
            msg = f"expected two-item price level, got {type(level).__name__}"
            raise TypeError(msg)
        levels.append((str(level[0]), str(level[1])))
    return levels


@dataclass(slots=True, frozen=True)
class Market:
    id: str
    status: str
    base_unit: str
    base_unit_precision: int
    min_base_amount: float
    quote_unit: str
    quote_unit_precision: int
    min_quote_amount: float
    m_wallet_supported: bool

    @classmethod
    def model_validate(cls, payload: object) -> Market:
        data = _expect_mapping(payload)
        return cls(
            id=_required_str(data, "id"),
            status=_required_str(data, "status"),
            base_unit=_required_str(data, "base_unit"),
            base_unit_precision=_required_int(data, "base_unit_precision"),
            min_base_amount=_required_float(data, "min_base_amount"),
            quote_unit=_required_str(data, "quote_unit"),
            quote_unit_precision=_required_int(data, "quote_unit_precision"),
            min_quote_amount=_required_float(data, "min_quote_amount"),
            m_wallet_supported=_required_bool(data, "m_wallet_supported"),
        )


class Staking(MaxBaseModel):
    stake_flag: bool
    unstake_flag: bool


class CurrencyNetwork(MaxBaseModel):
    token_contract_address: str | None
    precision: int
    id: str
    network_protocol: str
    network_congested: bool | str
    deposit_confirmations: int
    withdrawal_fee: float
    min_withdrawal_amount: float
    withdrawal_enabled: bool
    deposit_enabled: bool
    need_memo: bool


class Currency(MaxBaseModel):
    currency: str
    type: str
    precision: int
    m_wallet_supported: bool
    m_wallet_mortgageable: bool
    m_wallet_borrowable: bool
    min_borrow_amount: str
    networks: list[CurrencyNetwork]
    staking: Staking | None


@dataclass(slots=True, frozen=True)
class Timestamp:
    timestamp: int

    @classmethod
    def model_validate(cls, payload: object) -> Timestamp:
        data = _expect_mapping(payload)
        return cls(timestamp=_required_int(data, "timestamp"))


@dataclass(slots=True, frozen=True)
class KLine:
    timestamp: int
    open: str
    high: str
    low: str
    close: str
    volume: str


@dataclass(slots=True, frozen=True)
class Depth:
    timestamp: int
    asks: list[tuple[str, str]]
    bids: list[tuple[str, str]]
    last_update_version: int | None = None
    last_update_id: int | None = None

    @classmethod
    def model_validate(cls, payload: object) -> Depth:
        data = _expect_mapping(payload)
        return cls(
            timestamp=_required_int(data, "timestamp"),
            asks=_price_levels(data["asks"]),
            bids=_price_levels(data["bids"]),
            last_update_version=_optional_int(data, "last_update_version"),
            last_update_id=_optional_int(data, "last_update_id"),
        )


@dataclass(slots=True, frozen=True)
class PublicTrade:
    id: int
    price: str
    volume: str
    funds: str
    market: str
    side: str
    created_at: int

    @classmethod
    def model_validate(cls, payload: object) -> PublicTrade:
        data = _expect_mapping(payload)
        return cls(
            id=_required_int(data, "id"),
            price=_required_str(data, "price"),
            volume=_required_str(data, "volume"),
            funds=_required_str(data, "funds"),
            market=_required_str(data, "market"),
            side=_required_str(data, "side"),
            created_at=_required_int(data, "created_at"),
        )


@dataclass(slots=True, frozen=True)
class Account:
    currency: str
    balance: str
    locked: str
    staked: str | None = None
    principal: str | None = None
    interest: str | None = None

    @classmethod
    def model_validate(cls, payload: object) -> Account:
        data = _expect_mapping(payload)
        return cls(
            currency=_required_str(data, "currency"),
            balance=_required_str(data, "balance"),
            locked=_required_str(data, "locked"),
            staked=_optional_str(data, "staked"),
            principal=_optional_str(data, "principal"),
            interest=_optional_str(data, "interest"),
        )


class OrderSide(StrEnum):
    SELL = "sell"
    BUY = "buy"


class OrderState(StrEnum):
    WAIT = "wait"
    DONE = "done"
    CANCEL = "cancel"
    CONVERT = "convert"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    POST_ONLY = "post_only"
    IOC_LIMIT = "ioc_limit"


@dataclass(slots=True, frozen=True)
class Order:
    id: int
    wallet_type: str
    market: str
    client_oid: str | None = None
    group_id: int | None = None
    side: OrderSide = OrderSide.BUY
    state: OrderState = OrderState.WAIT
    ord_type: OrderType = OrderType.LIMIT
    price: str | None = None
    stop_price: str | None = None
    avg_price: str = ""
    volume: str = ""
    remaining_volume: str = ""
    executed_volume: str = ""
    trades_count: int = 0
    created_at: int = 0
    updated_at: int = 0

    @classmethod
    def model_validate(cls, payload: object) -> Order:
        data = _expect_mapping(payload)
        return cls(
            id=_required_int(data, "id"),
            wallet_type=_required_str(data, "wallet_type"),
            market=_required_str(data, "market"),
            client_oid=_optional_str(data, "client_oid"),
            group_id=_optional_int(data, "group_id"),
            side=OrderSide(data["side"]),
            state=OrderState(data["state"]),
            ord_type=OrderType(data["ord_type"]),
            price=_optional_str(data, "price"),
            stop_price=_optional_str(data, "stop_price"),
            avg_price=_required_str(data, "avg_price"),
            volume=_required_str(data, "volume"),
            remaining_volume=_required_str(data, "remaining_volume"),
            executed_volume=_required_str(data, "executed_volume"),
            trades_count=_required_int(data, "trades_count"),
            created_at=_required_int(data, "created_at"),
            updated_at=_required_int(data, "updated_at"),
        )


@dataclass(slots=True, frozen=True)
class PrivateTrade:
    id: int
    order_id: int
    wallet_type: str
    price: str
    volume: str
    funds: str
    market: str
    market_name: str
    side: str
    fee: str | None = None
    fee_currency: str | None = None
    fee_discounted: bool | None = None
    self_trade_bid_fee: str | None = None
    self_trade_bid_fee_currency: str | None = None
    self_trade_bid_fee_discounted: bool | None = None
    self_trade_bid_order_id: int | None = None
    liquidity: str = ""
    created_at: int = 0

    @classmethod
    def model_validate(cls, payload: object) -> PrivateTrade:
        data = _expect_mapping(payload)
        return cls(
            id=_required_int(data, "id"),
            order_id=_required_int(data, "order_id"),
            wallet_type=_required_str(data, "wallet_type"),
            price=_required_str(data, "price"),
            volume=_required_str(data, "volume"),
            funds=_required_str(data, "funds"),
            market=_required_str(data, "market"),
            market_name=_required_str(data, "market_name"),
            side=_required_str(data, "side"),
            fee=_optional_str(data, "fee"),
            fee_currency=_optional_str(data, "fee_currency"),
            fee_discounted=_optional_bool(data, "fee_discounted"),
            self_trade_bid_fee=_optional_str(data, "self_trade_bid_fee"),
            self_trade_bid_fee_currency=_optional_str(data, "self_trade_bid_fee_currency"),
            self_trade_bid_fee_discounted=_optional_bool(data, "self_trade_bid_fee_discounted"),
            self_trade_bid_order_id=_optional_int(data, "self_trade_bid_order_id"),
            liquidity=_required_str(data, "liquidity"),
            created_at=_required_int(data, "created_at"),
        )


@dataclass(slots=True, frozen=True)
class VipLevel:
    level: int
    minimum_trading_volume: int
    minimum_staking_volume: int
    maker_fee: float
    taker_fee: float

    @classmethod
    def model_validate(cls, payload: object) -> VipLevel:
        data = _expect_mapping(payload)
        return cls(
            level=_required_int(data, "level"),
            minimum_trading_volume=_required_int(data, "minimum_trading_volume"),
            minimum_staking_volume=_required_int(data, "minimum_staking_volume"),
            maker_fee=_required_float(data, "maker_fee"),
            taker_fee=_required_float(data, "taker_fee"),
        )


@dataclass(slots=True, frozen=True)
class UserInfo:
    email: str
    level: int
    current_vip_level: VipLevel
    next_vip_level: VipLevel | None
    m_wallet_enabled: bool | None = None

    @classmethod
    def model_validate(cls, payload: object) -> UserInfo:
        data = _expect_mapping(payload)
        next_vip_level = data.get("next_vip_level")
        return cls(
            email=_required_str(data, "email"),
            level=_required_int(data, "level"),
            current_vip_level=VipLevel.model_validate(data["current_vip_level"]),
            next_vip_level=None if next_vip_level is None else VipLevel.model_validate(next_vip_level),
            m_wallet_enabled=_optional_bool(data, "m_wallet_enabled"),
        )


@dataclass(slots=True, frozen=True)
class Withdrawal:
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

    @classmethod
    def model_validate(cls, payload: object) -> Withdrawal:
        data = _expect_mapping(payload)
        return cls(
            uuid=_required_str(data, "uuid"),
            currency=_required_str(data, "currency"),
            network_protocol=_optional_str(data, "network_protocol"),
            amount=_required_str(data, "amount"),
            fee=_required_str(data, "fee"),
            fee_currency=_required_str(data, "fee_currency"),
            to_address=_required_str(data, "to_address"),
            label=_required_str(data, "label"),
            txid=_optional_str(data, "txid"),
            created_at=_required_int(data, "created_at"),
            state=_required_str(data, "state"),
            transaction_type=_required_str(data, "transaction_type"),
        )


@dataclass(slots=True, frozen=True)
class WithdrawAddress:
    uuid: str
    currency: str
    network_protocol: str | None
    address: str
    extra_label: str
    created_at: int
    activated_at: int | None
    is_internal: bool
    network_congested: bool

    @classmethod
    def model_validate(cls, payload: object) -> WithdrawAddress:
        data = _expect_mapping(payload)
        return cls(
            uuid=_required_str(data, "uuid"),
            currency=_required_str(data, "currency"),
            network_protocol=_optional_str(data, "network_protocol"),
            address=_required_str(data, "address"),
            extra_label=_required_str(data, "extra_label"),
            created_at=_required_int(data, "created_at"),
            activated_at=_optional_int(data, "activated_at"),
            is_internal=_required_bool(data, "is_internal"),
            network_congested=_required_bool(data, "network_congested"),
        )


@dataclass(slots=True, frozen=True)
class Deposit:
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

    @classmethod
    def model_validate(cls, payload: object) -> Deposit:
        data = _expect_mapping(payload)
        return cls(
            uuid=_required_str(data, "uuid"),
            currency=_required_str(data, "currency"),
            network_protocol=_required_str(data, "network_protocol"),
            amount=_required_str(data, "amount"),
            to_address=_required_str(data, "to_address"),
            txid=_required_str(data, "txid"),
            created_at=_required_int(data, "created_at"),
            confirmations=_required_int(data, "confirmations"),
            state=_required_str(data, "state"),
            state_reason=_required_str(data, "state_reason"),
        )


@dataclass(slots=True, frozen=True)
class DepositAddress:
    currency: str
    network_protocol: str
    currency_version: str
    address: str | None

    @classmethod
    def model_validate(cls, payload: object) -> DepositAddress:
        data = _expect_mapping(payload)
        return cls(
            currency=_required_str(data, "currency"),
            network_protocol=_required_str(data, "network_protocol"),
            currency_version=_required_str(data, "currency_version"),
            address=_optional_str(data, "address"),
        )


@dataclass(slots=True, frozen=True)
class InternalTransfer:
    uuid: str
    currency: str
    amount: str
    created_at: int
    from_: str
    to: str
    state: str

    @classmethod
    def model_validate(cls, payload: object) -> InternalTransfer:
        data = _expect_mapping(payload)
        return cls(
            uuid=_required_str(data, "uuid"),
            currency=_required_str(data, "currency"),
            amount=_required_str(data, "amount"),
            created_at=_required_int(data, "created_at"),
            from_=_required_str(data, "from"),
            to=_required_str(data, "to"),
            state=_required_str(data, "state"),
        )


@dataclass(slots=True, frozen=True)
class Reward:
    uuid: str
    currency: str
    amount: str
    created_at: int
    type: str
    note: str

    @classmethod
    def model_validate(cls, payload: object) -> Reward:
        data = _expect_mapping(payload)
        return cls(
            uuid=_required_str(data, "uuid"),
            currency=_required_str(data, "currency"),
            amount=_required_str(data, "amount"),
            created_at=_required_int(data, "created_at"),
            type=_required_str(data, "type"),
            note=_required_str(data, "note"),
        )


@dataclass(slots=True, frozen=True)
class FundTransactionDeposit:
    sn: str
    is_internal: bool
    currency: str
    amount: str
    state: str
    created_at: int
    network_protocol: str | None
    to_address: str | None
    txid: str | None
    from_: str | None

    @classmethod
    def model_validate(cls, payload: object) -> FundTransactionDeposit:
        data = _expect_mapping(payload)
        return cls(
            sn=_required_str(data, "sn"),
            is_internal=_required_bool(data, "is_internal"),
            currency=_required_str(data, "currency"),
            amount=_required_str(data, "amount"),
            state=_required_str(data, "state"),
            created_at=_required_int(data, "created_at"),
            network_protocol=_optional_str(data, "network_protocol"),
            to_address=_optional_str(data, "to_address"),
            txid=_optional_str(data, "txid"),
            from_=_optional_str(data, "from"),
        )


@dataclass(slots=True, frozen=True)
class FundTransactionWithdrawal:
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

    @classmethod
    def model_validate(cls, payload: object) -> FundTransactionWithdrawal:
        data = _expect_mapping(payload)
        return cls(
            sn=_required_str(data, "sn"),
            is_internal=_required_bool(data, "is_internal"),
            currency=_required_str(data, "currency"),
            amount=_required_str(data, "amount"),
            state=_required_str(data, "state"),
            created_at=_required_int(data, "created_at"),
            network_protocol=_optional_str(data, "network_protocol"),
            fee=_optional_str(data, "fee"),
            fee_currency=_optional_str(data, "fee_currency"),
            to_address=_optional_str(data, "to_address"),
            label=_optional_str(data, "label"),
            txid=_optional_str(data, "txid"),
            to=_optional_str(data, "to"),
        )


@dataclass(slots=True, frozen=True)
class FundTransactionSource:
    platform: str
    sn: object
    wallet_type: str

    @classmethod
    def model_validate(cls, payload: object) -> FundTransactionSource:
        data = _expect_mapping(payload)
        return cls(
            platform=_required_str(data, "platform"),
            sn=data["sn"],
            wallet_type=_required_str(data, "wallet_type"),
        )


@dataclass(slots=True, frozen=True)
class FundTransactionTransfer:
    sn: str
    currency: str
    amount: str
    state: str
    created_at: int
    from_: FundTransactionSource
    to: FundTransactionSource

    @classmethod
    def model_validate(cls, payload: object) -> FundTransactionTransfer:
        data = _expect_mapping(payload)
        return cls(
            sn=_required_str(data, "sn"),
            currency=_required_str(data, "currency"),
            amount=_required_str(data, "amount"),
            state=_required_str(data, "state"),
            created_at=_required_int(data, "created_at"),
            from_=FundTransactionSource.model_validate(data["from"]),
            to=FundTransactionSource.model_validate(data["to"]),
        )


class ConvertOrder(MaxBaseModel):
    sn: str
    from_currency: str
    from_amount: str
    to_currency: str
    to_amount: str
    fee: str
    fee_currency: str
    fee_in_twd: str
    created_at: int


@dataclass(slots=True, frozen=True)
class Ticker:
    market: str
    at: int
    buy: str
    buy_vol: str
    sell: str
    sell_vol: str
    open: str
    low: str
    high: str
    last: str
    vol: str
    vol_in_btc: str
    vol_in_quote: str

    @classmethod
    def model_validate(cls, payload: object) -> Ticker:
        data = _expect_mapping(payload)
        return cls(
            market=_required_str(data, "market"),
            at=_required_int(data, "at"),
            buy=_required_str(data, "buy"),
            buy_vol=_required_str(data, "buy_vol"),
            sell=_required_str(data, "sell"),
            sell_vol=_required_str(data, "sell_vol"),
            open=_required_str(data, "open"),
            low=_required_str(data, "low"),
            high=_required_str(data, "high"),
            last=_required_str(data, "last"),
            vol=_required_str(data, "vol"),
            vol_in_btc=_required_str(data, "vol_in_btc"),
            vol_in_quote=_required_str(data, "vol_in_quote"),
        )


@dataclass(slots=True, frozen=True)
class HistoricalIndexPrice:
    timestamp: str
    price: str

    @classmethod
    def model_validate(cls, payload: object) -> HistoricalIndexPrice:
        data = _expect_mapping(payload)
        return cls(timestamp=_required_str(data, "timestamp"), price=_required_str(data, "price"))


@dataclass(slots=True, frozen=True)
class InterestRate:
    hourly_interest_rate: str
    next_hourly_interest_rate: str

    @classmethod
    def model_validate(cls, payload: object) -> InterestRate:
        data = _expect_mapping(payload)
        return cls(
            hourly_interest_rate=_required_str(data, "hourly_interest_rate"),
            next_hourly_interest_rate=_required_str(data, "next_hourly_interest_rate"),
        )


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
