from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from datetime import UTC
from datetime import datetime
from enum import StrEnum
from typing import Any
from typing import cast

import orjson

from maicoin.ws.balance import Balance
from maicoin.ws.channel import Channel
from maicoin.ws.kline import KLine
from maicoin.ws.m_wallet import MWalletADRatio
from maicoin.ws.m_wallet import MWalletBorrowing
from maicoin.ws.m_wallet import PoolQuota
from maicoin.ws.market_status import MarketStatus
from maicoin.ws.order import Order
from maicoin.ws.subscription import Subscription
from maicoin.ws.ticker import Ticker
from maicoin.ws.trade import Trade


class Event(StrEnum):
    ERROR = "error"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    AUTHENTICATED = "authenticated"
    SNAPSHOT = "snapshot"
    UPDATE = "update"
    ORDER_SNAPSHOT = "order_snapshot"
    ORDER_UPDATE = "order_update"
    TRADE_SNAPSHOT = "trade_snapshot"
    TRADE_UPDATE = "trade_update"
    ACCOUNT_SNAPSHOT = "account_snapshot"
    ACCOUNT_UPDATE = "account_update"
    FAST_TRADE_UPDATE = "fast_trade_update"
    MWALLET_ORDER_SNAPSHOT = "mwallet_order_snapshot"
    MWALLET_ORDER_UPDATE = "mwallet_order_update"
    MWALLET_TRADE_SNAPSHOT = "mwallet_trade_snapshot"
    MWALLET_TRADE_UPDATE = "mwallet_trade_update"
    MWALLET_FAST_TRADE_UPDATE = "mwallet_fast_trade_update"
    MWALLET_ACCOUNT_SNAPSHOT = "mwallet_account_snapshot"
    MWALLET_ACCOUNT_UPDATE = "mwallet_account_update"
    AD_RATIO_SNAPSHOT = "ad_ratio_snapshot"
    AD_RATIO_UPDATE = "ad_ratio_update"
    BORROWING_SNAPSHOT = "borrowing_snapshot"
    BORROWING_UPDATE = "borrowing_update"


# https://maicoin.github.io/max-websocket-docs/#/?id=response-key-alias
@dataclass(slots=True, frozen=True)
class Response:
    event: Event
    created_at: datetime
    id: str | None = None
    errors: list[str] | None = None
    subscriptions: list[Subscription] | None = None
    channel: Channel | None = None
    balances: list[Balance] | None = None
    market: str | None = None
    asks: list[list[str]] | None = None
    bids: list[list[str]] | None = None
    first_update_id: int | None = None
    last_update_id: int | None = None
    version: int | None = None
    orders: list[Order] | None = None
    ticker: Ticker | None = None
    trades: list[Trade] | None = None
    currency: str | None = None
    kline: KLine | None = None
    market_status: list[MarketStatus] | None = None
    pool_quota: PoolQuota | None = None
    m_wallet_ad_ratio: MWalletADRatio | None = None
    m_wallet_borrowings: list[MWalletBorrowing] | None = None

    @classmethod
    def model_validate_json(cls, payload: str | bytes | bytearray) -> Response:
        return cls.model_validate(orjson.loads(payload))

    @classmethod
    def model_validate(cls, payload: object) -> Response:
        data = _expect_mapping(payload)
        return cls(
            event=Event(data["e"]),
            created_at=_ms_datetime(data["T"]),
            id=_optional_str(data.get("i")),
            errors=_optional_str_list(data.get("E")),
            subscriptions=_optional_model_list(data.get("s"), Subscription.model_validate),
            channel=None if data.get("c") is None else Channel(data["c"]),
            balances=_optional_model_list(data.get("B"), Balance.model_validate),
            market=_optional_str(data.get("M")),
            asks=_optional_levels(data.get("a")),
            bids=_optional_levels(data.get("b")),
            first_update_id=_optional_int(data.get("fi")),
            last_update_id=_optional_int(data.get("li")),
            version=_optional_int(data.get("v")),
            orders=_optional_model_list(data.get("o"), Order.model_validate),
            ticker=_optional_model(data.get("tk"), Ticker.model_validate),
            trades=_optional_model_list(data.get("t"), Trade.model_validate),
            currency=_optional_str(data.get("cu")),
            kline=_optional_model(data.get("k"), KLine.model_validate),
            market_status=_optional_model_list(data.get("ms"), MarketStatus.model_validate),
            pool_quota=_optional_model(data.get("qta"), PoolQuota.model_validate),
            m_wallet_ad_ratio=_optional_model(data.get("ad"), MWalletADRatio.model_validate),
            m_wallet_borrowings=_optional_model_list(data.get("db"), MWalletBorrowing.model_validate),
        )

    def model_dump(self, *, exclude_none: bool = False) -> dict[str, object]:
        return cast("dict[str, object]", _dump(self, exclude_none=exclude_none))


def _expect_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        msg = f"expected mapping, got {type(payload).__name__}"
        raise TypeError(msg)
    return cast("Mapping[str, object]", payload)


def _ms_datetime(value: object) -> datetime:
    return datetime.fromtimestamp(int(cast("int | str | float", value)) / 1000, tz=UTC)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int | str | float):
        return int(value)
    msg = f"expected int-compatible value, got {type(value).__name__}"
    raise TypeError(msg)


def _optional_str_list(value: object) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        msg = f"expected list, got {type(value).__name__}"
        raise TypeError(msg)
    return [str(item) for item in value]


def _optional_levels(value: object) -> list[list[str]] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        msg = f"expected levels list, got {type(value).__name__}"
        raise TypeError(msg)
    levels: list[list[str]] = []
    for level in value:
        if not isinstance(level, list | tuple):
            msg = f"expected level list, got {type(level).__name__}"
            raise TypeError(msg)
        levels.append([str(item) for item in level])
    return levels


def _dump(value: object, *, exclude_none: bool) -> object:
    if value is None:
        return None
    if is_dataclass(value) and not isinstance(value, type):
        payload = {field.name: _dump(getattr(value, field.name), exclude_none=exclude_none) for field in fields(value)}
        if exclude_none:
            return {key: item for key, item in payload.items() if item is not None}
        return payload
    if isinstance(value, list):
        return [_dump(item, exclude_none=exclude_none) for item in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return cast("Any", model_dump)(exclude_none=exclude_none)
    return value


def _optional_model[T](value: object, parser: Callable[[object], T]) -> T | None:
    if value is None:
        return None
    return parser(value)


def _optional_model_list[T](value: object, parser: Callable[[object], T]) -> list[T] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        msg = f"expected list, got {type(value).__name__}"
        raise TypeError(msg)
    return [parser(item) for item in value]
