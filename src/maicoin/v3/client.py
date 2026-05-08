from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Protocol
from typing import cast
from urllib.parse import urljoin

import httpx

from .auth import build_auth_headers
from .auth import generate_nonce
from .errors import Response
from .errors import raise_for_api_error
from .errors import raise_for_response_status
from .models import Currency
from .models import Depth
from .models import HistoricalIndexPrice
from .models import InterestRate
from .models import KLine
from .models import Market
from .models import PublicTrade
from .models import Ticker
from .models import Timestamp

BASE_URL = "https://max-api.maicoin.com"
DEFAULT_TIMEOUT = 10


def _compact(params: Mapping[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in params.items() if value is not None}


class RequestSession(Protocol):
    def request(self, method: str, url: str, **kwargs: object) -> Response: ...


class Client:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: RequestSession | None = None,
        nonce_factory: Callable[[], int] = generate_nonce,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self.session: RequestSession = cast("RequestSession", httpx.Client()) if session is None else session
        self.nonce_factory = nonce_factory

    def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, object] | None = None,
        *,
        auth: bool = False,
    ) -> object:
        normalized_method = method.upper()
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = urljoin(self.base_url, normalized_path)
        request_params = dict(params or {})
        headers: dict[str, str] = {}

        if auth:
            if self.api_key is None or self.api_secret is None:
                msg = "api_key and api_secret are required for authenticated requests"
                raise ValueError(msg)
            headers.update(
                build_auth_headers(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    path=normalized_path,
                    params=request_params,
                    nonce=self.nonce_factory(),
                )
            )

        kwargs: dict[str, object] = {
            "headers": headers,
            "timeout": self.timeout,
        }
        if normalized_method == "GET":
            kwargs["params"] = request_params
        else:
            kwargs["json"] = request_params

        response = self.session.request(normalized_method, url, **kwargs)
        raise_for_response_status(response)
        if not response.content:
            return None

        payload = response.json()
        raise_for_api_error(payload)
        return payload

    def markets(self) -> list[Market]:
        payload = self.request("GET", "/api/v3/markets")
        return [Market.model_validate(item) for item in cast("list[object]", payload)]

    def currencies(self) -> list[Currency]:
        payload = self.request("GET", "/api/v3/currencies")
        return [Currency.model_validate(item) for item in cast("list[object]", payload)]

    def timestamp(self) -> Timestamp:
        payload = self.request("GET", "/api/v3/timestamp")
        return Timestamp.model_validate(payload)

    def kline(
        self,
        market: str,
        *,
        limit: int = 30,
        period: int = 1,
        timestamp: int | None = None,
    ) -> list[KLine]:
        payload = self.request(
            "GET",
            "/api/v3/k",
            params=_compact({"market": market, "limit": limit, "period": period, "timestamp": timestamp}),
        )
        return [
            KLine(
                timestamp=int(str(row[0])),
                open=str(row[1]),
                high=str(row[2]),
                low=str(row[3]),
                close=str(row[4]),
                volume=str(row[5]),
            )
            for row in cast("list[Sequence[object]]", payload)
        ]

    def depth(self, market: str, *, limit: int | None = None, sort_by_price: bool | None = None) -> Depth:
        payload = self.request(
            "GET",
            "/api/v3/depth",
            params=_compact({"market": market, "limit": limit, "sort_by_price": sort_by_price}),
        )
        return Depth.model_validate(payload)

    def trades(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        payload = self.request(
            "GET",
            "/api/v3/trades",
            params=_compact({"market": market, "timestamp": timestamp, "limit": limit}),
        )
        return [PublicTrade.model_validate(item) for item in cast("list[object]", payload)]

    def tickers(self, markets: Sequence[str]) -> list[Ticker]:
        payload = self.request("GET", "/api/v3/tickers", params={"markets[]": list(markets)})
        return [Ticker.model_validate(item) for item in cast("list[object]", payload)]

    def ticker(self, market: str) -> Ticker:
        payload = self.request("GET", "/api/v3/ticker", params={"market": market})
        return Ticker.model_validate(payload)

    def m_wallet_index_prices(self) -> dict[str, str]:
        payload = self.request("GET", "/api/v3/wallet/m/index_prices")
        return cast("dict[str, str]", payload)

    def m_wallet_historical_index_prices(
        self,
        market: str,
        *,
        start_time: int,
        end_time: int,
    ) -> list[HistoricalIndexPrice]:
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/historical_index_prices",
            params={"market": market, "start_time": start_time, "end_time": end_time},
        )
        return [HistoricalIndexPrice.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_limits(self) -> dict[str, str]:
        payload = self.request("GET", "/api/v3/wallet/m/limits")
        return cast("dict[str, str]", payload)

    def m_wallet_interest_rates(self) -> dict[str, InterestRate]:
        payload = self.request("GET", "/api/v3/wallet/m/interest_rates")
        return {
            currency: InterestRate.model_validate(rate) for currency, rate in cast("dict[str, object]", payload).items()
        }
