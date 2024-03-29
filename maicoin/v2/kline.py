from __future__ import annotations

from datetime import datetime
from urllib.parse import urljoin

import requests
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from requests.utils import default_headers

BASE_URL = "https://max-api.maicoin.com"
DEFAULT_TIMEOUT = 10


class KLine(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    @field_validator("timestamp", mode="before")
    @classmethod
    def convert_datetime(cls, v: int) -> datetime:
        return datetime.fromtimestamp(v)


class KLineRequest(BaseModel):
    market: str
    limit: int = Field(default=30)
    period: int = Field(default=1)
    timestamp: int | None = None

    def do(self) -> list[KLine]:
        resp = requests.get(
            urljoin(BASE_URL, "/api/v2/k"),
            params=self.model_dump(exclude_none=True),
            headers=default_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        return [
            KLine(
                timestamp=timestamp,
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
            for timestamp, open, high, low, close, volume in resp.json()
        ]
