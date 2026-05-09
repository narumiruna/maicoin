"""REST v3 client for the [MaiCoin MAX](https://max-api.maicoin.com/doc/v3.html) API.

Public endpoints (markets, tickers, depth, trades, kline, timestamp) need no
credentials. Every other method is authenticated and requires `api_key` /
`api_secret` to sign the request.
"""

# ruff: noqa: ANN401

from __future__ import annotations

import asyncio
import email.utils
import random
from collections.abc import AsyncIterator
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Protocol
from typing import cast
from urllib.parse import urljoin

import httpx

from maicoin.v3._endpoints import ConvertEndpoints
from maicoin.v3._endpoints import FundsEndpoints
from maicoin.v3._endpoints import MWalletEndpoints
from maicoin.v3._endpoints import OrderIntakeHistoryEndpoints
from maicoin.v3._endpoints import PublicMarketDataEndpoints
from maicoin.v3.auth import build_auth_headers
from maicoin.v3.auth import generate_nonce
from maicoin.v3.errors import Response
from maicoin.v3.errors import raise_for_api_error
from maicoin.v3.errors import raise_for_response_status
from maicoin.v3.models import Account
from maicoin.v3.models import ConvertOrder
from maicoin.v3.models import Currency
from maicoin.v3.models import Deposit
from maicoin.v3.models import DepositAddress
from maicoin.v3.models import Depth
from maicoin.v3.models import FundTransactionDeposit
from maicoin.v3.models import FundTransactionTransfer
from maicoin.v3.models import FundTransactionWithdrawal
from maicoin.v3.models import HistoricalIndexPrice
from maicoin.v3.models import InterestRate
from maicoin.v3.models import InternalTransfer
from maicoin.v3.models import KLine
from maicoin.v3.models import Market
from maicoin.v3.models import MWalletADRatio
from maicoin.v3.models import MWalletInterest
from maicoin.v3.models import MWalletLiquidation
from maicoin.v3.models import MWalletLiquidationDetail
from maicoin.v3.models import MWalletLoan
from maicoin.v3.models import MWalletRepayment
from maicoin.v3.models import MWalletTransfer
from maicoin.v3.models import Order
from maicoin.v3.models import OrderSide
from maicoin.v3.models import OrderType
from maicoin.v3.models import PrivateTrade
from maicoin.v3.models import PublicTrade
from maicoin.v3.models import Reward
from maicoin.v3.models import Ticker
from maicoin.v3.models import Timestamp
from maicoin.v3.models import UserInfo
from maicoin.v3.models import WithdrawAddress
from maicoin.v3.models import Withdrawal

BASE_URL = "https://max-api.maicoin.com"
"""Default MAX REST v3 base URL."""

DEFAULT_TIMEOUT = 10
"""Default per-request timeout in seconds."""

SAFE_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class RetryPolicy:
    """Conservative retry/rate-limit policy for REST requests.

    By default only idempotent public/read requests (`GET`, `HEAD`, `OPTIONS`)
    are retried. Private write endpoints can opt in with
    `retry_non_idempotent=True` when the caller has an idempotency strategy such
    as stable client order ids.
    """

    enabled: bool = True
    total_attempts: int = 3
    backoff_factor: float = 0.5
    max_delay: float = 10.0
    jitter: float = 0.25
    status_codes: frozenset[int] = frozenset({429, 502, 503, 504})
    retry_timeouts: bool = True
    retry_network_errors: bool = True
    retry_non_idempotent: bool = False
    respect_retry_after: bool = True

    def allows_method(self, method: str) -> bool:
        return method.upper() in SAFE_RETRY_METHODS or self.retry_non_idempotent

    def delay(self, attempt_index: int) -> float:
        delay = min(self.max_delay, self.backoff_factor * 2 ** max(0, attempt_index - 1))
        if self.jitter <= 0:
            return delay
        return delay + random.uniform(0, self.jitter)


def _retry_after_delay(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        retry_at = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=UTC)
    return max(0.0, (retry_at - datetime.now(UTC)).total_seconds())


class RequestSession(Protocol):
    """Minimal HTTP session protocol used by [`Client`][maicoin.v3.Client].

    Anything with a `request(method, url, **kwargs) -> Response` shape works,
    so you can swap in `httpx.AsyncClient`, a mocked session for tests, or a custom
    async transport.
    """

    async def request(self, method: str, url: str, **kwargs: object) -> Response: ...


class Client:
    """Async-first REST v3 client for the MaiCoin MAX exchange.

    Construct without credentials for public endpoints, or pass `api_key` and
    `api_secret` to call authenticated (signed) endpoints.

    Examples:
        Public-only client:

        >>> from maicoin.v3 import Client
        >>> async with Client() as client:  # doctest: +SKIP
        ...     await client.ticker("btctwd")

        Authenticated client:

        >>> async with Client(api_key="...", api_secret="...") as client:  # doctest: +SKIP
        ...     await client.accounts()
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: RequestSession | None = None,
        nonce_factory: Callable[[], int] = generate_nonce,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        """Build a REST v3 client.

        Args:
            api_key: MAX API access key. Required for authenticated endpoints.
            api_secret: MAX API secret used to sign authenticated requests.
            base_url: API base URL. Override for staging or test environments.
            timeout: Per-request timeout in seconds.
            session: Custom HTTP session implementing [`RequestSession`][maicoin.v3.client.RequestSession].
                Defaults to a fresh `httpx.AsyncClient`.
            nonce_factory: Callable returning a strictly increasing integer
                nonce in milliseconds. Override in tests.
            retry_policy: Retry/backoff policy for transient failures. Pass
                `RetryPolicy(enabled=False)` to disable retries.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self._owns_session = session is None
        self._session: RequestSession | None = session
        self.nonce_factory = nonce_factory
        self.retry_policy = retry_policy or RetryPolicy()
        self._market_data = PublicMarketDataEndpoints(self)
        self._orders = OrderIntakeHistoryEndpoints(self)
        self._funds = FundsEndpoints(self)
        self._convert = ConvertEndpoints(self)
        self._m_wallet = MWalletEndpoints(self)

    @property
    def session(self) -> RequestSession:
        """Underlying async HTTP session, created lazily for default clients."""
        if self._session is None:
            self._session = cast("RequestSession", httpx.AsyncClient())
        return self._session

    @session.setter
    def session(self, session: RequestSession) -> None:
        self._session = session

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying async HTTP session when it supports closing."""
        if self._session is None:
            return
        aclose = getattr(self._session, "aclose", None)
        if aclose is not None:
            await aclose()
        if self._owns_session:
            self._session = None

    def _run_sync(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Run one async REST method for synchronous scripts."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            msg = (
                "Synchronous Client.*_sync wrappers cannot run inside an active event loop; "
                "await the async method instead."
            )
            raise RuntimeError(msg)

        method = getattr(self, method_name)
        if not self._owns_session:
            return asyncio.run(method(*args, **kwargs))

        async def runner() -> Any:
            self._session = cast("RequestSession", httpx.AsyncClient())
            try:
                return await method(*args, **kwargs)
            finally:
                await self.aclose()

        return asyncio.run(runner())

    def request_sync(
        self, method: str, path: str, params: Mapping[str, object] | None = None, *, auth: bool = False
    ) -> object:
        """Synchronous convenience wrapper."""
        return self._run_sync("request", method, path, params, auth=auth)

    def markets_sync(self) -> list[Market]:
        """Synchronous convenience wrapper."""
        return self._run_sync("markets")

    def currencies_sync(self) -> list[Currency]:
        """Synchronous convenience wrapper."""
        return self._run_sync("currencies")

    def timestamp_sync(self) -> Timestamp:
        """Synchronous convenience wrapper."""
        return self._run_sync("timestamp")

    def kline_sync(self, market: str, *, limit: int = 30, period: int = 1, timestamp: int | None = None) -> list[KLine]:
        """Synchronous convenience wrapper."""
        return self._run_sync("kline", market, limit=limit, period=period, timestamp=timestamp)

    def depth_sync(self, market: str, *, limit: int | None = None, sort_by_price: bool | None = None) -> Depth:
        """Synchronous convenience wrapper."""
        return self._run_sync("depth", market, limit=limit, sort_by_price=sort_by_price)

    def trades_sync(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        """Synchronous convenience wrapper."""
        return self._run_sync("trades", market, timestamp=timestamp, limit=limit)

    def tickers_sync(self, markets: Sequence[str]) -> list[Ticker]:
        """Synchronous convenience wrapper."""
        return self._run_sync("tickers", markets)

    def ticker_sync(self, market: str) -> Ticker:
        """Synchronous convenience wrapper."""
        return self._run_sync("ticker", market)

    def info_sync(self) -> UserInfo:
        """Synchronous convenience wrapper."""
        return self._run_sync("info")

    def accounts_sync(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
        """Synchronous convenience wrapper."""
        return self._run_sync("accounts", wallet_type=wallet_type, currency=currency)

    def wallet_trades_sync(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        from_id: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[PrivateTrade]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "wallet_trades",
            wallet_type=wallet_type,
            market=market,
            timestamp=timestamp,
            from_id=from_id,
            order=order,
            limit=limit,
        )

    def open_orders_sync(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "open_orders", wallet_type=wallet_type, market=market, timestamp=timestamp, order_by=order_by, limit=limit
        )

    def closed_orders_sync(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "closed_orders", wallet_type=wallet_type, market=market, timestamp=timestamp, order_by=order_by, limit=limit
        )

    def order_history_sync(
        self, market: str, *, wallet_type: str = "spot", from_id: int | None = None, limit: int | None = None
    ) -> list[Order]:
        """Synchronous convenience wrapper."""
        return self._run_sync("order_history", market, wallet_type=wallet_type, from_id=from_id, limit=limit)

    def order_sync(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Synchronous convenience wrapper."""
        return self._run_sync("order", order_id=order_id, client_oid=client_oid)

    def create_order_sync(
        self,
        market: str,
        side: OrderSide | str,
        volume: str,
        *,
        wallet_type: str = "spot",
        price: str | None = None,
        client_oid: str | None = None,
        stop_price: str | None = None,
        ord_type: OrderType | str | None = None,
        group_id: int | None = None,
    ) -> Order:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "create_order",
            market,
            side,
            volume,
            wallet_type=wallet_type,
            price=price,
            client_oid=client_oid,
            stop_price=stop_price,
            ord_type=ord_type,
            group_id=group_id,
        )

    def cancel_order_sync(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Synchronous convenience wrapper."""
        return self._run_sync("cancel_order", order_id=order_id, client_oid=client_oid)

    def cancel_orders_sync(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        side: OrderSide | str | None = None,
        group_id: int | None = None,
    ) -> list[Order]:
        """Synchronous convenience wrapper."""
        return self._run_sync("cancel_orders", wallet_type=wallet_type, market=market, side=side, group_id=group_id)

    def order_trades_sync(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        """Synchronous convenience wrapper."""
        return self._run_sync("order_trades", order_id=order_id, client_oid=client_oid)

    def withdrawal_sync(self, uuid: str) -> Withdrawal:
        """Synchronous convenience wrapper."""
        return self._run_sync("withdrawal", uuid)

    def create_withdrawal_sync(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        """Synchronous convenience wrapper."""
        return self._run_sync("create_withdrawal", withdraw_address_uuid=withdraw_address_uuid, amount=amount)

    def create_twd_withdrawal_sync(self, amount: str) -> Withdrawal:
        """Synchronous convenience wrapper."""
        return self._run_sync("create_twd_withdrawal", amount)

    def withdrawals_sync(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Withdrawal]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "withdrawals", currency=currency, state=state, timestamp=timestamp, order=order, limit=limit
        )

    def withdraw_addresses_sync(
        self, currency: str, *, limit: int | None = None, offset: int | None = None
    ) -> list[WithdrawAddress]:
        """Synchronous convenience wrapper."""
        return self._run_sync("withdraw_addresses", currency, limit=limit, offset=offset)

    def deposit_sync(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
        """Synchronous convenience wrapper."""
        return self._run_sync("deposit", txid=txid, uuid=uuid)

    def deposits_sync(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Deposit]:
        """Synchronous convenience wrapper."""
        return self._run_sync("deposits", currency=currency, timestamp=timestamp, order=order, limit=limit)

    def deposit_address_sync(self, currency_version: str) -> DepositAddress:
        """Synchronous convenience wrapper."""
        return self._run_sync("deposit_address", currency_version)

    def internal_transfers_sync(
        self,
        side: str,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[InternalTransfer]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "internal_transfers", side, currency=currency, timestamp=timestamp, order=order, limit=limit
        )

    def rewards_sync(
        self,
        *,
        reward_type: str | None = None,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Reward]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "rewards", reward_type=reward_type, currency=currency, timestamp=timestamp, order=order, limit=limit
        )

    def fund_transaction_deposits_sync(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionDeposit]:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_deposits", timestamp=timestamp, order=order, limit=limit)

    def fund_transaction_deposit_sync(self, sn: str) -> FundTransactionDeposit:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_deposit", sn)

    def fund_transaction_withdrawals_sync(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_withdrawals", timestamp=timestamp, order=order, limit=limit)

    def fund_transaction_withdrawal_sync(self, sn: str) -> FundTransactionWithdrawal:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_withdrawal", sn)

    def fund_transaction_transfers_sync(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_transfers", timestamp=timestamp, order=order, limit=limit)

    def fund_transaction_transfer_sync(self, sn: str) -> FundTransactionTransfer:
        """Synchronous convenience wrapper."""
        return self._run_sync("fund_transaction_transfer", sn)

    def create_convert_sync(
        self, *, from_currency: str, to_currency: str, from_amount: str | None = None, to_amount: str | None = None
    ) -> ConvertOrder:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "create_convert",
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=from_amount,
            to_amount=to_amount,
        )

    def convert_sync(self, sn: str) -> ConvertOrder:
        """Synchronous convenience wrapper."""
        return self._run_sync("convert", sn)

    def converts_sync(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        """Synchronous convenience wrapper."""
        return self._run_sync("converts", timestamp=timestamp, order=order, limit=limit)

    def m_wallet_index_prices_sync(self) -> dict[str, str]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_index_prices")

    def m_wallet_historical_index_prices_sync(
        self, market: str, *, start_time: int, end_time: int
    ) -> list[HistoricalIndexPrice]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_historical_index_prices", market, start_time=start_time, end_time=end_time)

    def m_wallet_limits_sync(self) -> dict[str, str]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_limits")

    def m_wallet_interest_rates_sync(self) -> dict[str, InterestRate]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_interest_rates")

    def create_m_wallet_loan_sync(self, *, currency: str, amount: str) -> MWalletLoan:
        """Synchronous convenience wrapper."""
        return self._run_sync("create_m_wallet_loan", currency=currency, amount=amount)

    def m_wallet_loans_sync(
        self, currency: str, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLoan]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_loans", currency, timestamp=timestamp, order=order, limit=limit)

    def create_m_wallet_transfer_sync(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
        """Synchronous convenience wrapper."""
        return self._run_sync("create_m_wallet_transfer", currency=currency, amount=amount, side=side)

    def m_wallet_transfers_sync(
        self,
        *,
        currency: str,
        side: str,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletTransfer]:
        """Synchronous convenience wrapper."""
        return self._run_sync(
            "m_wallet_transfers", currency=currency, side=side, timestamp=timestamp, order=order, limit=limit
        )

    def create_m_wallet_repayment_sync(self, *, currency: str, amount: str) -> MWalletRepayment:
        """Synchronous convenience wrapper."""
        return self._run_sync("create_m_wallet_repayment", currency=currency, amount=amount)

    def m_wallet_repayments_sync(
        self, currency: str, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletRepayment]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_repayments", currency, timestamp=timestamp, order=order, limit=limit)

    def m_wallet_liquidations_sync(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLiquidation]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_liquidations", timestamp=timestamp, order=order, limit=limit)

    def m_wallet_liquidation_sync(self, sn: str) -> MWalletLiquidationDetail:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_liquidation", sn)

    def m_wallet_interests_sync(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletInterest]:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_interests", currency=currency, timestamp=timestamp, order=order, limit=limit)

    def m_wallet_ad_ratio_sync(self) -> MWalletADRatio:
        """Synchronous convenience wrapper."""
        return self._run_sync("m_wallet_ad_ratio")

    async def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, object] | None = None,
        *,
        auth: bool = False,
    ) -> object:
        """Send a raw REST v3 request and return the parsed JSON payload.

        Use this escape hatch when you need an endpoint that the typed
        wrappers below don't cover. Auth headers, nonce injection, and error
        handling work the same way as for the typed methods.

        Args:
            method: HTTP method, case-insensitive (e.g. `"GET"`, `"POST"`).
            path: Request path. Leading `/` is added automatically.
            params: Query parameters (GET) or JSON body (other methods).
                Use `None` values to omit a key — they are dropped before sending.
            auth: When `True`, sign the request with the configured credentials.

        Returns:
            The parsed JSON response, or `None` for empty bodies.

        Raises:
            ValueError: `auth=True` but the client has no credentials.
            MaxHTTPError: Non-2xx HTTP response.
            MaxAPIError: MAX-shaped error payload (`{"error": {...}}`).
        """
        normalized_method = method.upper()
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = urljoin(self.base_url, normalized_path)
        request_params = dict(params or {})
        headers: dict[str, str] = {}

        if auth:
            if self.api_key is None or self.api_secret is None:
                msg = "api_key and api_secret are required for authenticated requests"
                raise ValueError(msg)
            nonce = self.nonce_factory()
            request_params = {"nonce": nonce, **request_params}
            headers.update(
                build_auth_headers(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    path=normalized_path,
                    params=request_params,
                    nonce=nonce,
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

        response = await self._request_with_retries(normalized_method, url, kwargs)
        raise_for_response_status(response)
        if not response.content:
            return None

        payload = response.json()
        raise_for_api_error(payload)
        return payload

    async def _request_with_retries(self, method: str, url: str, kwargs: Mapping[str, object]) -> Response:
        policy = self.retry_policy
        attempts = max(1, policy.total_attempts)
        retry_allowed = policy.enabled and policy.allows_method(method) and attempts > 1
        last_exc: httpx.TimeoutException | httpx.TransportError | None = None

        for attempt_index in range(1, attempts + 1):
            try:
                response = await self.session.request(method, url, **dict(kwargs))
            except httpx.TimeoutException as exc:
                last_exc = exc
                if not (retry_allowed and policy.retry_timeouts and attempt_index < attempts):
                    raise
                await self._sleep_before_retry(policy.delay(attempt_index))
                continue
            except httpx.TransportError as exc:
                last_exc = exc
                if not (retry_allowed and policy.retry_network_errors and attempt_index < attempts):
                    raise
                await self._sleep_before_retry(policy.delay(attempt_index))
                continue

            if not (retry_allowed and response.status_code in policy.status_codes and attempt_index < attempts):
                return response

            retry_after = None
            if policy.respect_retry_after:
                headers = getattr(response, "headers", None)
                retry_after = _retry_after_delay(headers.get("Retry-After") if headers is not None else None)
            await self._sleep_before_retry(retry_after if retry_after is not None else policy.delay(attempt_index))

        if last_exc is not None:
            raise last_exc
        msg = "request retry loop exhausted without a response"
        raise RuntimeError(msg)

    async def _sleep_before_retry(self, delay: float) -> None:
        if delay > 0:
            await asyncio.sleep(delay)

    async def markets(self) -> list[Market]:
        """List all available markets (`GET /api/v3/markets`)."""
        return await self._market_data.markets()

    async def currencies(self) -> list[Currency]:
        """List all supported currencies, including network info (`GET /api/v3/currencies`)."""
        return await self._market_data.currencies()

    async def timestamp(self) -> Timestamp:
        """Return the server-side timestamp (`GET /api/v3/timestamp`)."""
        return await self._market_data.timestamp()

    async def kline(
        self,
        market: str,
        *,
        limit: int = 30,
        period: int = 1,
        timestamp: int | None = None,
    ) -> list[KLine]:
        """Fetch OHLCV candles for `market` (`GET /api/v3/k`)."""
        return await self._market_data.kline(market, limit=limit, period=period, timestamp=timestamp)

    async def depth(self, market: str, *, limit: int | None = None, sort_by_price: bool | None = None) -> Depth:
        """Fetch the order book depth for `market` (`GET /api/v3/depth`)."""
        return await self._market_data.depth(market, limit=limit, sort_by_price=sort_by_price)

    async def trades(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        """Fetch recent public trades for `market` (`GET /api/v3/trades`)."""
        return await self._market_data.trades(market, timestamp=timestamp, limit=limit)

    async def tickers(self, markets: Sequence[str]) -> list[Ticker]:
        """Fetch tickers for several markets in one request (`GET /api/v3/tickers`)."""
        return await self._market_data.tickers(markets)

    async def ticker(self, market: str) -> Ticker:
        """Fetch the ticker for a single market (`GET /api/v3/ticker`)."""
        return await self._market_data.ticker(market)

    async def info(self) -> UserInfo:
        """Return the authenticated user profile and VIP info (`GET /api/v3/info`)."""
        return await self._orders.info()

    async def accounts(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
        """List wallet account balances."""
        return await self._orders.accounts(wallet_type=wallet_type, currency=currency)

    async def wallet_trades(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        from_id: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[PrivateTrade]:
        """List the authenticated user's trades for a wallet."""
        return await self._orders.wallet_trades(
            wallet_type=wallet_type,
            market=market,
            timestamp=timestamp,
            from_id=from_id,
            order=order,
            limit=limit,
        )

    async def open_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List the user's open orders."""
        return await self._orders.open_orders(
            wallet_type=wallet_type, market=market, timestamp=timestamp, order_by=order_by, limit=limit
        )

    async def closed_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List the user's closed (filled or cancelled) orders."""
        return await self._orders.closed_orders(
            wallet_type=wallet_type, market=market, timestamp=timestamp, order_by=order_by, limit=limit
        )

    async def order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """Page through the full order history for a market."""
        return await self._orders.order_history(market, wallet_type=wallet_type, from_id=from_id, limit=limit)

    async def iter_wallet_trades(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        from_id: int | None = None,
        order: str = "asc",
        page_limit: int = 100,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[PrivateTrade]:
        """Iterate wallet trades using the `from_id` cursor."""
        async for trade in self._orders.iter_wallet_trades(
            wallet_type=wallet_type,
            market=market,
            timestamp=timestamp,
            from_id=from_id,
            order=order,
            page_limit=page_limit,
            max_items=max_items,
            max_pages=max_pages,
        ):
            yield trade

    async def iter_order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        page_limit: int = 100,
        max_items: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[Order]:
        """Iterate order history using the `from_id` cursor."""
        async for order_item in self._orders.iter_order_history(
            market,
            wallet_type=wallet_type,
            from_id=from_id,
            page_limit=page_limit,
            max_items=max_items,
            max_pages=max_pages,
        ):
            yield order_item

    async def order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Fetch a single order by `order_id` or `client_oid`."""
        return await self._orders.order(order_id=order_id, client_oid=client_oid)

    async def create_order(
        self,
        market: str,
        side: OrderSide | str,
        volume: str,
        *,
        wallet_type: str = "spot",
        price: str | None = None,
        client_oid: str | None = None,
        stop_price: str | None = None,
        ord_type: OrderType | str | None = None,
        group_id: int | None = None,
    ) -> Order:
        """Place a new order."""
        return await self._orders.create_order(
            market,
            side,
            volume,
            wallet_type=wallet_type,
            price=price,
            client_oid=client_oid,
            stop_price=stop_price,
            ord_type=ord_type,
            group_id=group_id,
        )

    async def cancel_order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Cancel an order by `order_id` or `client_oid`."""
        return await self._orders.cancel_order(order_id=order_id, client_oid=client_oid)

    async def cancel_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        side: OrderSide | str | None = None,
        group_id: int | None = None,
    ) -> list[Order]:
        """Bulk-cancel orders. Filters compose: omit them all to cancel everything in the wallet."""
        return await self._orders.cancel_orders(wallet_type=wallet_type, market=market, side=side, group_id=group_id)

    async def order_trades(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        """List the executed trades for one order."""
        return await self._orders.order_trades(order_id=order_id, client_oid=client_oid)

    async def withdrawal(self, uuid: str) -> Withdrawal:
        """Look up a withdrawal by its `uuid`."""
        return await self._funds.withdrawal(uuid)

    async def create_withdrawal(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        """Submit a crypto withdrawal to a pre-approved address."""
        return await self._funds.create_withdrawal(withdraw_address_uuid=withdraw_address_uuid, amount=amount)

    async def create_twd_withdrawal(self, amount: str) -> Withdrawal:
        """Submit a TWD bank withdrawal."""
        return await self._funds.create_twd_withdrawal(amount)

    async def withdrawals(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Withdrawal]:
        """List withdrawal history."""
        return await self._funds.withdrawals(
            currency=currency, state=state, timestamp=timestamp, order=order, limit=limit
        )

    async def withdraw_addresses(
        self,
        currency: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WithdrawAddress]:
        """List the user's whitelisted withdrawal addresses for `currency`."""
        return await self._funds.withdraw_addresses(currency, limit=limit, offset=offset)

    async def deposit(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
        """Look up a deposit by `txid` or `uuid`."""
        return await self._funds.deposit(txid=txid, uuid=uuid)

    async def deposits(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Deposit]:
        """List deposit history."""
        return await self._funds.deposits(currency=currency, timestamp=timestamp, order=order, limit=limit)

    async def deposit_address(self, currency_version: str) -> DepositAddress:
        """Get the deposit address for a specific currency/network version."""
        return await self._funds.deposit_address(currency_version)

    async def internal_transfers(
        self,
        side: str,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[InternalTransfer]:
        """List internal transfers between MAX users."""
        return await self._funds.internal_transfers(
            side, currency=currency, timestamp=timestamp, order=order, limit=limit
        )

    async def rewards(
        self,
        *,
        reward_type: str | None = None,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Reward]:
        """List reward history (referrals, mining, staking, etc.)."""
        return await self._funds.rewards(
            reward_type=reward_type, currency=currency, timestamp=timestamp, order=order, limit=limit
        )

    async def fund_transaction_deposits(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionDeposit]:
        """List fund-transaction deposits (off-exchange settlement)."""
        return await self._funds.fund_transaction_deposits(timestamp=timestamp, order=order, limit=limit)

    async def fund_transaction_deposit(self, sn: str) -> FundTransactionDeposit:
        """Look up a fund-transaction deposit by `sn`."""
        return await self._funds.fund_transaction_deposit(sn)

    async def fund_transaction_withdrawals(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        """List fund-transaction withdrawals."""
        return await self._funds.fund_transaction_withdrawals(timestamp=timestamp, order=order, limit=limit)

    async def fund_transaction_withdrawal(self, sn: str) -> FundTransactionWithdrawal:
        """Look up a fund-transaction withdrawal by `sn`."""
        return await self._funds.fund_transaction_withdrawal(sn)

    async def fund_transaction_transfers(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        """List fund-transaction transfers."""
        return await self._funds.fund_transaction_transfers(timestamp=timestamp, order=order, limit=limit)

    async def fund_transaction_transfer(self, sn: str) -> FundTransactionTransfer:
        """Look up a fund-transaction transfer by `sn`."""
        return await self._funds.fund_transaction_transfer(sn)

    async def create_convert(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
    ) -> ConvertOrder:
        """Submit a convert order between two currencies."""
        return await self._convert.create_convert(
            from_currency=from_currency, to_currency=to_currency, from_amount=from_amount, to_amount=to_amount
        )

    async def convert(self, sn: str) -> ConvertOrder:
        """Look up a convert order by `sn`."""
        return await self._convert.convert(sn)

    async def converts(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        """List convert order history."""
        return await self._convert.converts(timestamp=timestamp, order=order, limit=limit)

    async def m_wallet_index_prices(self) -> dict[str, str]:
        """Return current M-Wallet index prices keyed by market id."""
        return await self._m_wallet.m_wallet_index_prices()

    async def m_wallet_historical_index_prices(
        self,
        market: str,
        *,
        start_time: int,
        end_time: int,
    ) -> list[HistoricalIndexPrice]:
        """Fetch historical M-Wallet index prices for `market`."""
        return await self._m_wallet.m_wallet_historical_index_prices(market, start_time=start_time, end_time=end_time)

    async def m_wallet_limits(self) -> dict[str, str]:
        """Return per-currency M-Wallet borrow limits."""
        return await self._m_wallet.m_wallet_limits()

    async def m_wallet_interest_rates(self) -> dict[str, InterestRate]:
        """Return current M-Wallet interest rates per currency."""
        return await self._m_wallet.m_wallet_interest_rates()

    async def create_m_wallet_loan(self, *, currency: str, amount: str) -> MWalletLoan:
        """Borrow `amount` of `currency` into the M-Wallet."""
        return await self._m_wallet.create_m_wallet_loan(currency=currency, amount=amount)

    async def m_wallet_loans(
        self, currency: str, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLoan]:
        """List M-Wallet loans for `currency`."""
        return await self._m_wallet.m_wallet_loans(currency, timestamp=timestamp, order=order, limit=limit)

    async def create_m_wallet_transfer(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
        """Transfer between spot and M-Wallet."""
        return await self._m_wallet.create_m_wallet_transfer(currency=currency, amount=amount, side=side)

    async def m_wallet_transfers(
        self,
        *,
        currency: str,
        side: str,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletTransfer]:
        """List M-Wallet transfer history."""
        return await self._m_wallet.m_wallet_transfers(
            currency=currency, side=side, timestamp=timestamp, order=order, limit=limit
        )

    async def create_m_wallet_repayment(self, *, currency: str, amount: str) -> MWalletRepayment:
        """Repay an M-Wallet loan."""
        return await self._m_wallet.create_m_wallet_repayment(currency=currency, amount=amount)

    async def m_wallet_repayments(
        self, currency: str, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletRepayment]:
        """List M-Wallet repayment history for `currency`."""
        return await self._m_wallet.m_wallet_repayments(currency, timestamp=timestamp, order=order, limit=limit)

    async def m_wallet_liquidations(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLiquidation]:
        """List M-Wallet liquidation events."""
        return await self._m_wallet.m_wallet_liquidations(timestamp=timestamp, order=order, limit=limit)

    async def m_wallet_liquidation(self, sn: str) -> MWalletLiquidationDetail:
        """Look up a single M-Wallet liquidation, including order/repayment details."""
        return await self._m_wallet.m_wallet_liquidation(sn)

    async def m_wallet_interests(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletInterest]:
        """List M-Wallet interest accruals."""
        return await self._m_wallet.m_wallet_interests(currency=currency, timestamp=timestamp, order=order, limit=limit)

    async def m_wallet_ad_ratio(self) -> MWalletADRatio:
        """Return the M-Wallet account debt ratio (asset-to-debt and margin level)."""
        return await self._m_wallet.m_wallet_ad_ratio()
