from __future__ import annotations

import hmac
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List

from ..enums import ActionType
from ..enums import Filter
from .subscription import Subscription


def create_authorize_action(api_key, api_secret) -> Action:
    nonce = int(datetime.now().timestamp() * 1000)

    signature = hmac.new(api_secret.encode(), digestmod="sha256")
    signature.update(str(nonce).encode())
    signature = signature.hexdigest()

    return Action(
        action=ActionType.Authorize,
        id=str(uuid.uuid4()),
        api_key=api_key,
        signature=signature,
        nonce=nonce,
    )


def create_subscribe_action(subscriptions: List[Subscription]):
    return Action(
        action=ActionType.Subscribe,
        id=str(uuid.uuid4()),
        subscriptions=subscriptions,
    )


@dataclass
class Action:
    action: ActionType
    id: str
    api_key: str = None
    nonce: int = None
    signature: str = None
    filters: List[Filter] = None
    subscriptions: List[Subscription] = None

    def to_dict(self) -> dict:
        d = dict(
            action=self.action.value,
            apiKey=self.api_key,
            nonce=self.nonce,
            signature=self.signature,
            id=self.id,
        )

        if self.subscriptions:
            d["subscriptions"] = [s.to_dict() for s in self.subscriptions]

        if self.filters:
            d["filters"] = [f.value for f in self.filters]

        return d
