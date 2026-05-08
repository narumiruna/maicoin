from __future__ import annotations

import hmac
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from enum import StrEnum
from typing import Any

import orjson

from maicoin.ws.subscription import Subscription


class Action(StrEnum):
    Subscribe = "sub"
    Authorize = "auth"
    Unsubscribe = "unsub"


class Filter(StrEnum):
    ORDER = "order"
    TRADE = "trade"
    ACCOUNT = "account"
    TRADE_UPDATE = "trade_update"
    MWALLET_ORDER = "mwallet_order"
    MWALLET_TRADE = "mwallet_trade"
    MWALLET_FAST_TRADE_UPDATE = "mwallet_fast_trade_update"
    MWALLET_ACCOUNT = "mwallet_account"
    AD_RATIO = "ad_ratio"
    BORROWING = "borrowing"


@dataclass(slots=True, frozen=True)
class Request:
    action: Action
    id: str
    api_key: str | None = None
    nonce: int | None = None
    signature: str | None = None
    filters: list[Filter] | None = None
    subscriptions: list[Subscription] | None = None
    subscription: list[Subscription] | None = None

    @classmethod
    def model_validate(cls, payload: Mapping[str, object]) -> Request:
        return cls(
            action=Action(payload["action"]),
            id=str(payload["id"]),
            api_key=_optional_str(payload.get("apiKey", payload.get("api_key"))),
            nonce=_optional_int(payload.get("nonce")),
            signature=_optional_str(payload.get("signature")),
            filters=_parse_filters(payload.get("filters")),
            subscriptions=_parse_subscriptions(payload.get("subscriptions")),
            subscription=_parse_subscriptions(payload.get("subscription")),
        )

    @classmethod
    def auth(cls, api_key: str, api_secret: str) -> Request:
        nonce = int(datetime.now(tz=UTC).timestamp() * 1000)

        signature = hmac.new(api_secret.encode(), digestmod="sha256")
        signature.update(str(nonce).encode())
        signature = signature.hexdigest()

        return cls(
            action=Action.Authorize,
            id=str(uuid.uuid4()),
            api_key=api_key,
            signature=signature,
            nonce=nonce,
        )

    @classmethod
    def subscribe(cls, subscriptions: list[Subscription]) -> Request:
        return cls(
            action=Action.Subscribe,
            id=str(uuid.uuid4()),
            subscriptions=subscriptions,
        )

    @classmethod
    def unsubscribe(cls, subscriptions: list[Subscription]) -> Request:
        return cls(
            action=Action.Unsubscribe,
            id=str(uuid.uuid4()),
            subscription=subscriptions,
        )

    def message(self) -> str:
        return orjson.dumps(self.to_payload()).decode()

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"action": self.action, "id": self.id}
        if self.api_key is not None:
            payload["apiKey"] = self.api_key
        if self.nonce is not None:
            payload["nonce"] = self.nonce
        if self.signature is not None:
            payload["signature"] = self.signature
        if self.filters is not None:
            payload["filters"] = self.filters
        if self.subscriptions is not None:
            payload["subscriptions"] = [_subscription_payload(subscription) for subscription in self.subscriptions]
        if self.subscription is not None:
            payload["subscription"] = [_subscription_payload(subscription) for subscription in self.subscription]
        return payload


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


def _parse_filters(value: object) -> list[Filter] | None:
    if value is None:
        return None
    return [Filter(item) for item in _expect_list(value)]


def _parse_subscriptions(value: object) -> list[Subscription] | None:
    if value is None:
        return None
    return [
        item if isinstance(item, Subscription) else Subscription.model_validate(item) for item in _expect_list(value)
    ]


def _expect_list(value: object) -> list[Any]:
    if not isinstance(value, list):
        msg = f"expected list, got {type(value).__name__}"
        raise TypeError(msg)
    return value


def _subscription_payload(subscription: Subscription) -> dict[str, object]:
    return subscription.model_dump(exclude_none=True)
