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

    def info(self) -> UserInfo:
        payload = self.request("GET", "/api/v3/info", auth=True)
        return UserInfo.model_validate(payload)

    def accounts(self, *, wallet_type: str = "spot", currency: str | None = None) -> list[Account]:
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
        payload = self.request(
            "GET",
            f"/api/v3/wallet/{wallet_type}/orders/history",
            params=_compact({"market": market, "from_id": from_id, "limit": limit}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def order(self, *, order_id: int | None = None, client_oid: str | None = None) -> Order:
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
        payload = self.request(
            "DELETE",
            f"/api/v3/wallet/{wallet_type}/orders",
            params=_compact({"market": market, "side": side, "group_id": group_id}),
            auth=True,
        )
        return [Order.model_validate(item) for item in cast("list[object]", payload)]

    def order_trades(self, *, order_id: int | None = None, client_oid: str | None = None) -> list[PrivateTrade]:
        payload = self.request(
            "GET",
            "/api/v3/order/trades",
            params=_compact({"order_id": order_id, "client_oid": client_oid}),
            auth=True,
        )
        return [PrivateTrade.model_validate(item) for item in cast("list[object]", payload)]

    def withdrawal(self, uuid: str) -> Withdrawal:
        payload = self.request("GET", "/api/v3/withdrawal", params={"uuid": uuid}, auth=True)
        return Withdrawal.model_validate(payload)

    def create_withdrawal(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        payload = self.request(
            "POST",
            "/api/v3/withdrawal",
            params={"withdraw_address_uuid": withdraw_address_uuid, "amount": amount},
            auth=True,
        )
        return Withdrawal.model_validate(payload)

    def create_twd_withdrawal(self, amount: str) -> Withdrawal:
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
        payload = self.request(
            "GET",
            "/api/v3/withdraw_addresses",
            params=_compact({"currency": currency, "limit": limit, "offset": offset}),
            auth=True,
        )
        return [WithdrawAddress.model_validate(item) for item in cast("list[object]", payload)]

    def deposit(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
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
        payload = self.request(
            "GET",
            "/api/v3/deposits",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [Deposit.model_validate(item) for item in cast("list[object]", payload)]

    def deposit_address(self, currency_version: str) -> DepositAddress:
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
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/deposits",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionDeposit.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_deposit(self, sn: str) -> FundTransactionDeposit:
        payload = self.request("GET", "/api/v3/fund_transactions/deposit", params={"sn": sn}, auth=True)
        return FundTransactionDeposit.model_validate(payload)

    def fund_transaction_withdrawals(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/withdrawals",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionWithdrawal.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_withdrawal(self, sn: str) -> FundTransactionWithdrawal:
        payload = self.request("GET", "/api/v3/fund_transactions/withdrawal", params={"sn": sn}, auth=True)
        return FundTransactionWithdrawal.model_validate(payload)

    def fund_transaction_transfers(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        payload = self.request(
            "GET",
            "/api/v3/fund_transactions/transfers",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionTransfer.model_validate(item) for item in cast("list[object]", payload)]

    def fund_transaction_transfer(self, sn: str) -> FundTransactionTransfer:
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
        payload = self.request("GET", "/api/v3/convert", params={"sn": sn}, auth=True)
        return ConvertOrder.model_validate(payload)

    def converts(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        payload = self.request(
            "GET",
            "/api/v3/converts",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [ConvertOrder.model_validate(item) for item in cast("list[object]", payload)]

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

    def create_m_wallet_loan(self, *, currency: str, amount: str) -> MWalletLoan:
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
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/loans",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLoan.model_validate(item) for item in cast("list[object]", payload)]

    def create_m_wallet_transfer(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
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
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/liquidations",
            params=_compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLiquidation.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_liquidation(self, sn: str) -> MWalletLiquidationDetail:
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
        payload = self.request(
            "GET",
            "/api/v3/wallet/m/interests",
            params=_compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletInterest.model_validate(item) for item in cast("list[object]", payload)]

    def m_wallet_ad_ratio(self) -> MWalletADRatio:
        payload = self.request("GET", "/api/v3/wallet/m/ad_ratio", auth=True)
        return MWalletADRatio.model_validate(payload)
