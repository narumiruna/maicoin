"""REST v3 client for the [MaiCoin MAX](https://max-api.maicoin.com/doc/v3.html) API.

Public endpoints (markets, tickers, depth, trades, kline, timestamp) need no
credentials. Every other method is authenticated and requires `api_key` /
`api_secret` to sign the request.
"""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Protocol
from typing import cast
from urllib.parse import urljoin

import httpx

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


def _compact(params: Mapping[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in params.items() if value is not None}


class RequestSession(Protocol):
    """Minimal HTTP session protocol used by [`Client`][maicoin.v3.Client].

    Anything with a `request(method, url, **kwargs) -> Response` shape works,
    so you can swap in `httpx.Client`, a mocked session for tests, or a custom
    transport.
    """

    def request(self, method: str, url: str, **kwargs: object) -> Response: ...


class Client:
    """Synchronous REST v3 client for the MaiCoin MAX exchange.

    Construct without credentials for public endpoints, or pass `api_key` and
    `api_secret` to call authenticated (signed) endpoints.

    Examples:
        Public-only client:

        >>> from maicoin.v3 import Client
        >>> client = Client()
        >>> client.ticker("btctwd")  # doctest: +SKIP

        Authenticated client:

        >>> client = Client(api_key="...", api_secret="...")  # doctest: +SKIP
        >>> client.accounts()  # doctest: +SKIP
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
    ) -> None:
        """Build a REST v3 client.

        Args:
            api_key: MAX API access key. Required for authenticated endpoints.
            api_secret: MAX API secret used to sign authenticated requests.
            base_url: API base URL. Override for staging or test environments.
            timeout: Per-request timeout in seconds.
            session: Custom HTTP session implementing [`RequestSession`][maicoin.v3.client.RequestSession].
                Defaults to a fresh `httpx.Client`.
            nonce_factory: Callable returning a strictly increasing integer
                nonce in milliseconds. Override in tests.
        """
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

        response = self.session.request(normalized_method, url, **kwargs)
        raise_for_response_status(response)
        if not response.content:
            return None

        payload = response.json()
        raise_for_api_error(payload)
        return payload

    def markets(self) -> list[Market]:
        """List all available markets (`GET /api/v3/markets`)."""
        payload = self.request("GET", "/api/v3/markets")
        return [Market.model_validate(item) for item in cast("list[object]", payload)]

    def currencies(self) -> list[Currency]:
        """List all supported currencies, including network info (`GET /api/v3/currencies`)."""
        payload = self.request("GET", "/api/v3/currencies")
        return [Currency.model_validate(item) for item in cast("list[object]", payload)]

    def timestamp(self) -> Timestamp:
        """Return the server-side timestamp (`GET /api/v3/timestamp`)."""
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
        """Fetch OHLCV candles for `market` (`GET /api/v3/k`).

        Args:
            market: Market id, e.g. `"btctwd"`.
            limit: Number of candles to return (1-10000, default 30).
            period: Candle period in minutes (1, 5, 15, 30, 60, 120, 240, 360, 720, 1440, 4320, 10080).
            timestamp: Earliest UNIX timestamp (seconds) to include.
        """
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
        """Fetch the order book depth for `market` (`GET /api/v3/depth`).

        Args:
            market: Market id, e.g. `"btctwd"`.
            limit: Maximum number of price levels per side.
            sort_by_price: If `True`, sort each side by price.
        """
        payload = self.request(
            "GET",
            "/api/v3/depth",
            params=_compact({"market": market, "limit": limit, "sort_by_price": sort_by_price}),
        )
        return Depth.model_validate(payload)

    def trades(self, market: str, *, timestamp: int | None = None, limit: int | None = None) -> list[PublicTrade]:
        """Fetch recent public trades for `market` (`GET /api/v3/trades`)."""
        payload = self.request(
            "GET",
            "/api/v3/trades",
            params=_compact({"market": market, "timestamp": timestamp, "limit": limit}),
        )
        return [PublicTrade.model_validate(item) for item in cast("list[object]", payload)]

    def tickers(self, markets: Sequence[str]) -> list[Ticker]:
        """Fetch tickers for several markets in one request (`GET /api/v3/tickers`)."""
        payload = self.request("GET", "/api/v3/tickers", params={"markets[]": list(markets)})
        return [Ticker.model_validate(item) for item in cast("list[object]", payload)]

    def ticker(self, market: str) -> Ticker:
        """Fetch the ticker for a single market (`GET /api/v3/ticker`)."""
        payload = self.request("GET", "/api/v3/ticker", params={"market": market})
        return Ticker.model_validate(payload)

    def info(self) -> UserInfo:
        """Return the authenticated user profile and VIP info (`GET /api/v3/info`)."""
        payload = self.request("GET", "/api/v3/info", auth=True)
        return UserInfo.model_validate(payload)

    def accounts(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
        """List wallet account balances.

        Args:
            wallet_type: `"spot"` or `"m"` (M-Wallet).
            currency: Optional filter, e.g. `"twd"`.
        """
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/accounts",
            params=_compact({"currency": currency}),
            auth=True,
        )
        return [Account.model_validate(item) for item in cast("list[object]", payload)]

    def wallet_trades(
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
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/trades",
            params=_compact(
                {"market": market, "timestamp": timestamp, "from_id": from_id, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [PrivateTrade.model_validate(item) for item in cast("list[object]", payload)]

    def open_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List the user's open orders."""
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/open",
            params=_compact({"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def closed_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        timestamp: int | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """List the user's closed (filled or cancelled) orders."""
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/closed",
            params=_compact({"market": market, "timestamp": timestamp, "order_by": order_by, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def order_history(
        self,
        market: str,
        *,
        wallet_type: str = "spot",
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[Order]:
        """Page through the full order history for a market.

        Use `from_id` to seek past the last id you saw.
        """
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/history",
            params=_compact({"market": market, "from_id": from_id, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Fetch a single order by `order_id` or `client_oid`."""
        payload = self.request(
            "GET",
            "/api/v3/order",
            params=_compact({"id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return Order.model_validate(payload)

    def create_order(
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
        """Place a new order.

        !!! warning
            This is a state-changing endpoint. Double-check `market`, `side`,
            `volume`, and `price` before calling against a live account.

        Args:
            market: Market id, e.g. `"btctwd"`.
            side: `"buy"` or `"sell"` (or [`OrderSide`][maicoin.v3.OrderSide]).
            volume: Order amount as a decimal string.
            wallet_type: `"spot"` or `"m"`.
            price: Limit price. Omit for market orders.
            client_oid: Optional client-side order id for idempotency.
            stop_price: Trigger price for stop orders.
            ord_type: One of [`OrderType`][maicoin.v3.OrderType] (e.g. `"limit"`, `"market"`, `"stop_limit"`).
            group_id: Group id for OCO/grouped cancellation.
        """
        payload = self.request(
            "POST",
            f"/api/v3/wallet/{wallet_type}/order",
            params=_compact(
                {
                    "market": market,
                    "side": side,
                    "volume": volume,
                    "price": price,
                    "client_oid": client_oid,
                    "stop_price": stop_price,
                    "ord_type": ord_type,
                    "group_id": group_id,
                }
            ),
            auth=True,
        )
        return Order.model_validate(payload)

    def cancel_order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
        """Cancel an order by `order_id` or `client_oid`."""
        payload = self.request(
            "DELETE",
            "/api/v3/order",
            params=_compact({"id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return Order.model_validate(payload)

    def cancel_orders(
        self,
        *,
        wallet_type: str = "spot",
        market: str | None = None,
        side: OrderSide | str | None = None,
        group_id: int | None = None,
    ) -> list[Order]:
        """Bulk-cancel orders. Filters compose: omit them all to cancel everything in the wallet."""
        payload = self.request(
            "DELETE",
            f"/api/v3/wallet/{wallet_type}/orders",
            params=_compact({"market": market, "side": side, "group_id": group_id}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def order_trades(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        """List the executed trades for one order."""
        payload = self.request(
            "GET",
            "/api/v3/order/trades",
            params=_compact({"order_id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return [PrivateTrade.model_validate(item) for item in cast("list[object]", payload)]

    def withdrawal(self, uuid: str) -> Withdrawal:
        """Look up a withdrawal by its `uuid`."""
        payload = self.request("GET", "/api/v3/withdrawal", params={"uuid": uuid}, auth=True)
        return Withdrawal.model_validate(payload)

    def create_withdrawal(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        """Submit a crypto withdrawal to a pre-approved address.

        !!! warning
            State-changing. The address must already be whitelisted on MAX.
        """
        payload = self.request(
            "POST",
            "/api/v3/withdrawal",
            params={"withdraw_address_uuid": withdraw_address_uuid, "amount": amount},
            auth=True,
        )
        return Withdrawal.model_validate(payload)

    def create_twd_withdrawal(self, amount: str) -> Withdrawal:
        """Submit a TWD bank withdrawal.

        !!! warning
            State-changing. The default bank account on file is debited.
        """
        payload = self.request("POST", "/api/v3/withdrawal/twd", params={"amount": amount}, auth=True)
        return Withdrawal.model_validate(payload)

    def withdrawals(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Withdrawal]:
        """List withdrawal history."""
        payload = self.request(
            "GET",
            "/api/v3/withdrawals",
            params=_compact(
                {"currency": currency, "state": state, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [Withdrawal.model_validate(item) for item in cast("list[object]", payload)]

    def withdraw_addresses(
        self,
        currency: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WithdrawAddress]:
        """List the user's whitelisted withdrawal addresses for `currency`."""
        payload = self.request(
            "GET",
            "/api/v3/withdraw_addresses",
            params=_compact({"currency": currency, "limit": limit, "offset": offset}),
            auth=True,
        )
        return [WithdrawAddress.model_validate(item) for item in cast("list[object]", payload)]

    def deposit(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
        """Look up a deposit by `txid` or `uuid`."""
        payload = self.request("GET", "/api/v3/deposit", params=_compact({"txid": txid, "uuid": uuid}), auth=True)
        return Deposit.model_validate(payload)

    def deposits(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Deposit]:
        """List deposit history."""
        payload = self.request(
            "GET",
            "/api/v3/deposits",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [Deposit.model_validate(item) for item in cast("list[object]", payload)]

    def deposit_address(self, currency_version: str) -> DepositAddress:
        """Get the deposit address for a specific currency/network version."""
        payload = self.request(
            "GET",
            "/api/v3/deposit_address",
            params={"currency_version": currency_version},
            auth=True,
        )
        return DepositAddress.model_validate(payload)

    def internal_transfers(
        self,
        side: str,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[InternalTransfer]:
        """List internal transfers between MAX users.

        Args:
            side: `"in"` or `"out"`.
        """
        payload = self.request(
            "GET",
            "/api/v3/internal_transfers",
            params=_compact(
                {"side": side, "currency": currency, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [InternalTransfer.model_validate(item) for item in cast("list[object]", payload)]

    def rewards(
        self,
        *,
        reward_type: str | None = None,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Reward]:
        """List reward history (referrals, mining, staking, etc.)."""
        payload = self.request(
            "GET",
            "/api/v3/rewards",
            params=_compact(
                {
                    "reward_type": reward_type,
                    "currency": currency,
                    "timestamp": timestamp,
                    "order": order,
                    "limit": limit,
                }
            ),
            auth=True,
        )
        return [Reward.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_deposits(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionDeposit]:
        """List fund-transaction deposits (off-exchange settlement)."""
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/deposits",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionDeposit.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_deposit(self, sn: str) -> FundTransactionDeposit:
        """Look up a fund-transaction deposit by `sn`."""
        payload = self.request("GET", "/api/v3/fund_transactions/deposit", params={"sn": sn}, auth=True)
        return FundTransactionDeposit.model_validate(payload)

    def fund_transaction_withdrawals(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        """List fund-transaction withdrawals."""
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/withdrawals",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionWithdrawal.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_withdrawal(self, sn: str) -> FundTransactionWithdrawal:
        """Look up a fund-transaction withdrawal by `sn`."""
        payload = self.request("GET", "/api/v3/fund_transactions/withdrawal", params={"sn": sn}, auth=True)
        return FundTransactionWithdrawal.model_validate(payload)

    def fund_transaction_transfers(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        """List fund-transaction transfers."""
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/transfers",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionTransfer.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_transfer(self, sn: str) -> FundTransactionTransfer:
        """Look up a fund-transaction transfer by `sn`."""
        payload = self.request("GET", "/api/v3/fund_transactions/transfer", params={"sn": sn}, auth=True)
        return FundTransactionTransfer.model_validate(payload)

    def create_convert(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
    ) -> ConvertOrder:
        """Submit a convert order between two currencies.

        Specify exactly one of `from_amount` or `to_amount`.
        """
        payload = self.request(
            "POST",
            "/api/v3/convert",
            params=_compact(
                {
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "from_amount": from_amount,
                    "to_amount": to_amount,
                }
            ),
            auth=True,
        )
        return ConvertOrder.model_validate(payload)

    def convert(self, sn: str) -> ConvertOrder:
        """Look up a convert order by `sn`."""
        payload = self.request("GET", "/api/v3/convert", params={"sn": sn}, auth=True)
        return ConvertOrder.model_validate(payload)

    def converts(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        """List convert order history."""
        payload = self.request(
            "GET",
            "/api/v3/converts",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [ConvertOrder.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_index_prices(self) -> dict[str, str]:
        """Return current M-Wallet index prices keyed by market id."""
        payload = self.request("GET", "/api/v3/wallet/m/index_prices")
        return cast("dict[str, str]", payload)

    def m_wallet_historical_index_prices(
        self,
        market: str,
        *,
        start_time: int,
        end_time: int,
    ) -> list[HistoricalIndexPrice]:
        """Fetch historical M-Wallet index prices for `market`.

        Args:
            market: Market id.
            start_time: Inclusive start (UNIX milliseconds).
            end_time: Inclusive end (UNIX milliseconds).
        """
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/historical_index_prices",
            params={"market": market, "start_time": start_time, "end_time": end_time},
        )
        return [HistoricalIndexPrice.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_limits(self) -> dict[str, str]:
        """Return per-currency M-Wallet borrow limits."""
        payload = self.request("GET", "/api/v3/wallet/m/limits")
        return cast("dict[str, str]", payload)

    def m_wallet_interest_rates(self) -> dict[str, InterestRate]:
        """Return current M-Wallet interest rates per currency."""
        payload = self.request("GET", "/api/v3/wallet/m/interest_rates")
        return {
            currency: InterestRate.model_validate(rate) for currency, rate in cast("dict[str, object]", payload).items()
        }

    def create_m_wallet_loan(self, *, currency: str, amount: str) -> MWalletLoan:
        """Borrow `amount` of `currency` into the M-Wallet.

        !!! warning
            State-changing — accrues interest until repaid.
        """
        payload = self.request(
            "POST",
            "/api/v3/wallet/m/loan",
            params={"currency": currency, "amount": amount},
            auth=True,
        )
        return MWalletLoan.model_validate(payload)

    def m_wallet_loans(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletLoan]:
        """List M-Wallet loans for `currency`."""
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/loans",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLoan.model_validate(item) for item in cast("list[object]", payload)]

    def create_m_wallet_transfer(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
        """Transfer between spot and M-Wallet.

        Args:
            currency: Currency code.
            amount: Decimal amount as a string.
            side: `"in"` (spot → M-Wallet) or `"out"` (M-Wallet → spot).
        """
        payload = self.request(
            "POST",
            "/api/v3/wallet/m/transfer",
            params={"currency": currency, "amount": amount, "side": side},
            auth=True,
        )
        return MWalletTransfer.model_validate(payload)

    def m_wallet_transfers(
        self,
        *,
        currency: str,
        side: str,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletTransfer]:
        """List M-Wallet transfer history."""
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/transfers",
            params=_compact(
                {"currency": currency, "side": side, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [MWalletTransfer.model_validate(item) for item in cast("list[object]", payload)]

    def create_m_wallet_repayment(self, *, currency: str, amount: str) -> MWalletRepayment:
        """Repay an M-Wallet loan.

        !!! warning
            State-changing.
        """
        payload = self.request(
            "POST",
            "/api/v3/wallet/m/repayment",
            params={"currency": currency, "amount": amount},
            auth=True,
        )
        return MWalletRepayment.model_validate(payload)

    def m_wallet_repayments(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletRepayment]:
        """List M-Wallet repayment history for `currency`."""
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/repayments",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletRepayment.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_liquidations(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLiquidation]:
        """List M-Wallet liquidation events."""
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/liquidations",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLiquidation.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_liquidation(self, sn: str) -> MWalletLiquidationDetail:
        """Look up a single M-Wallet liquidation, including order/repayment details."""
        payload = self.request("GET", "/api/v3/wallet/m/liquidation", params={"sn": sn}, auth=True)
        return MWalletLiquidationDetail.model_validate(payload)

    def m_wallet_interests(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletInterest]:
        """List M-Wallet interest accruals."""
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/interests",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletInterest.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_ad_ratio(self) -> MWalletADRatio:
        """Return the M-Wallet account debt ratio (asset-to-debt and margin level)."""
        payload = self.request("GET", "/api/v3/wallet/m/ad_ratio", auth=True)
        return MWalletADRatio.model_validate(payload)
