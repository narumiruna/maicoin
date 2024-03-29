from __future__ import annotations

import hmac
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from .subscription import Subscription


class Action(str, Enum):
    Subscribe = "sub"
    Authorize = "auth"
    Unsubscribe = "unsub"


class Filter(str, Enum):
    ORDER = "order"
    TRADE = "trade"
    ACCOUNT = "account"
    TRADE_UPDATE = "trade_update"


class Request(BaseModel):
    action: Action
    id: str
    api_key: str | None = Field(default=None, serialization_alias="apiKey")
    nonce: int | None = None
    signature: str | None = None
    filters: list[Filter] | None = None
    subscriptions: list[Subscription] | None = None

    @classmethod
    def auth(cls, api_key: str, api_secret: str) -> Request:
        nonce = int(datetime.now().timestamp() * 1000)

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
            subscriptions=subscriptions,
        )

    def message(self) -> str:
        return self.model_dump_json(by_alias=True, exclude_none=True)
