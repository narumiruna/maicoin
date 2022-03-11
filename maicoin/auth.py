from __future__ import annotations

import hmac
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from .utils import get_api_key_from_env, get_api_secret_from_env


class Filter(Enum):
    ORDER = 'order'
    TRADE = 'trade'
    ACCOUNT = 'account'
    TRADE_UPDATE = 'trade_update'


@dataclass
class Auth:
    api_key: str
    nonce: int
    signature: str
    filters: List[Filter] = None

    @classmethod
    def from_env(cls) -> Auth:
        api_key = get_api_key_from_env()
        api_secret = get_api_secret_from_env()

        nonce = int(datetime.now().timestamp() * 1000)

        signature = hmac.new(api_secret.encode(), digestmod='sha256')
        signature.update(str(nonce).encode())
        signature = signature.hexdigest()

        return cls(
            api_key=api_key,
            signature=signature,
            nonce=nonce,
        )

    def to_msg(self) -> dict:
        d = {
            'action': 'auth',
            'apiKey': self.api_key,
            'nonce': self.nonce,
            'signature': self.signature,
            'id': str(uuid.uuid4()),
        }

        if self.filters:
            d['filters'] = [f.value for f in self.filters]

        return d
