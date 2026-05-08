from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict


class MaxBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class Market(MaxBaseModel):
    id: str
    status: str
    base_unit: str
    base_unit_precision: int
    min_base_amount: float
    quote_unit: str
    quote_unit_precision: int
    min_quote_amount: float
    m_wallet_supported: bool


class Staking(MaxBaseModel):
    stake_flag: bool
    unstake_flag: bool


class CurrencyNetwork(MaxBaseModel):
    token_contract_address: str
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


class Timestamp(MaxBaseModel):
    timestamp: int


class KLine(MaxBaseModel):
    timestamp: int
    open: str
    high: str
    low: str
    close: str
    volume: str


class Depth(MaxBaseModel):
    timestamp: int
    asks: list[tuple[str, str]]
    bids: list[tuple[str, str]]
    last_update_version: int | None = None
    last_update_id: int | None = None


class PublicTrade(MaxBaseModel):
    id: int
    price: str
    volume: str
    funds: str
    market: str
    side: str
    created_at: int


class Account(MaxBaseModel):
    currency: str
    balance: str
    locked: str
    staked: str | None = None
    principal: str | None = None
    interest: str | None = None


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


class Order(MaxBaseModel):
    id: int
    wallet_type: str
    market: str
    client_oid: str | None = None
    group_id: int | None = None
    side: OrderSide
    state: OrderState
    ord_type: OrderType
    price: str | None = None
    stop_price: str | None = None
    avg_price: str
    volume: str
    remaining_volume: str
    executed_volume: str
    trades_count: int
    created_at: int
    updated_at: int


class PrivateTrade(MaxBaseModel):
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
    liquidity: str
    created_at: int


class VipLevel(MaxBaseModel):
    level: int
    minimum_trading_volume: int
    minimum_staking_volume: int
    maker_fee: float
    taker_fee: float


class UserInfo(MaxBaseModel):
    email: str
    level: int
    current_vip_level: VipLevel
    next_vip_level: VipLevel | None
    m_wallet_enabled: bool | None = None


class Ticker(MaxBaseModel):
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


class HistoricalIndexPrice(MaxBaseModel):
    timestamp: str
    price: str


class InterestRate(MaxBaseModel):
    hourly_interest_rate: str
    next_hourly_interest_rate: str
