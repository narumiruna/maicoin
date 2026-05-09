from __future__ import annotations

from enum import StrEnum

from maicoin.v3.models.base import MaxBaseModel


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
