"""WebSocket outgoing request models (subscribe, unsubscribe, auth)."""

from __future__ import annotations

import hmac
import uuid
from datetime import UTC
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field

from maicoin.ws.subscription import Subscription


class Action(StrEnum):
    """Action verb sent in the `action` field of a WebSocket request."""

    Subscribe = "sub"
    """Add subscriptions to the connection."""
    Authorize = "auth"
    """Authenticate the connection so private channels become available."""
    Unsubscribe = "unsub"
    """Remove existing subscriptions."""


class Filter(StrEnum):
    """Optional filters for subscription requests.

    Filters narrow private channels to a specific event family, e.g. only
    `order` updates without trade or account events.
    """

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


class Request(BaseModel):
    """A single outbound WebSocket request.

    Use the [`subscribe`][maicoin.ws.Request.subscribe],
    [`unsubscribe`][maicoin.ws.Request.unsubscribe], and
    [`auth`][maicoin.ws.Request.auth] class methods rather than constructing
    `Request` directly — they fill in the correct `action`, generate `id`,
    and (for auth) compute the HMAC signature.
    """

    action: Action
    """Verb describing what this request does."""
    id: str
    """Client-generated request id, echoed back in the matching response."""
    api_key: str | None = Field(default=None, serialization_alias="apiKey")
    """MAX API access key. Serialized as `apiKey`."""
    nonce: int | None = None
    """Auth nonce in milliseconds."""
    signature: str | None = None
    """`HMAC-SHA256(api_secret, str(nonce))` hex digest."""
    filters: list[Filter] | None = None
    """Optional [`Filter`][maicoin.ws.Filter] list narrowing private channels."""
    subscriptions: list[Subscription] | None = None
    """Subscriptions for `sub` requests."""
    subscription: list[Subscription] | None = None
    """Subscriptions for `unsub` requests. Note: MAX uses the singular key here."""

    @classmethod
    def auth(cls, api_key: str, api_secret: str) -> Request:
        """Build an `auth` request signed with `api_secret`.

        The signature is `HMAC-SHA256(api_secret, str(nonce))` where `nonce`
        is the current UTC time in milliseconds.
        """
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
        """Build a `sub` request adding `subscriptions` to the connection."""
        return cls(
            action=Action.Subscribe,
            id=str(uuid.uuid4()),
            subscriptions=subscriptions,
        )

    @classmethod
    def unsubscribe(cls, subscriptions: list[Subscription]) -> Request:
        """Build an `unsub` request removing `subscriptions`."""
        return cls(
            action=Action.Unsubscribe,
            id=str(uuid.uuid4()),
            subscription=subscriptions,
        )

    def message(self) -> str:
        """Serialize this request as a JSON string ready to send over the socket.

        Empty fields are dropped and `api_key` is rendered as `apiKey` to
        match the MAX wire format.
        """
        return self.model_dump_json(by_alias=True, exclude_none=True)
