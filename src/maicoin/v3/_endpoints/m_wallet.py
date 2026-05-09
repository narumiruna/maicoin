"""M-Wallet REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3.models.m_wallet import HistoricalIndexPrice
from maicoin.v3.models.m_wallet import InterestRate
from maicoin.v3.models.m_wallet import MWalletADRatio
from maicoin.v3.models.m_wallet import MWalletInterest
from maicoin.v3.models.m_wallet import MWalletLiquidation
from maicoin.v3.models.m_wallet import MWalletLiquidationDetail
from maicoin.v3.models.m_wallet import MWalletLoan
from maicoin.v3.models.m_wallet import MWalletRepayment
from maicoin.v3.models.m_wallet import MWalletTransfer

M_WALLET_INDEX_PRICES = EndpointSpec("GET", "/api/v3/wallet/m/index_prices")
M_WALLET_HISTORICAL_INDEX_PRICES = EndpointSpec("GET", "/api/v3/wallet/m/historical_index_prices")
M_WALLET_LIMITS = EndpointSpec("GET", "/api/v3/wallet/m/limits")
M_WALLET_INTEREST_RATES = EndpointSpec("GET", "/api/v3/wallet/m/interest_rates")
CREATE_M_WALLET_LOAN = EndpointSpec("POST", "/api/v3/wallet/m/loan", auth=True)
M_WALLET_LOANS = EndpointSpec("GET", "/api/v3/wallet/m/loans", auth=True)
CREATE_M_WALLET_TRANSFER = EndpointSpec("POST", "/api/v3/wallet/m/transfer", auth=True)
M_WALLET_TRANSFERS = EndpointSpec("GET", "/api/v3/wallet/m/transfers", auth=True)
CREATE_M_WALLET_REPAYMENT = EndpointSpec("POST", "/api/v3/wallet/m/repayment", auth=True)
M_WALLET_REPAYMENTS = EndpointSpec("GET", "/api/v3/wallet/m/repayments", auth=True)
M_WALLET_LIQUIDATIONS = EndpointSpec("GET", "/api/v3/wallet/m/liquidations", auth=True)
M_WALLET_LIQUIDATION = EndpointSpec("GET", "/api/v3/wallet/m/liquidation", auth=True)
M_WALLET_INTERESTS = EndpointSpec("GET", "/api/v3/wallet/m/interests", auth=True)
M_WALLET_AD_RATIO = EndpointSpec("GET", "/api/v3/wallet/m/ad_ratio", auth=True)


@dataclass(frozen=True, slots=True)
class MWalletEndpoints:
    """M-Wallet public and authenticated request/parse rules."""

    requester: RestRequester

    @property
    def endpoint(self) -> EndpointExecutor:
        return EndpointExecutor(self.requester)

    async def m_wallet_index_prices(self) -> dict[str, str]:
        payload = await self.endpoint.raw(M_WALLET_INDEX_PRICES)
        return cast("dict[str, str]", payload)

    async def m_wallet_historical_index_prices(
        self,
        market: str,
        *,
        start_time: int,
        end_time: int,
    ) -> list[HistoricalIndexPrice]:
        return await self.endpoint.model_list(
            M_WALLET_HISTORICAL_INDEX_PRICES,
            HistoricalIndexPrice,
            {"market": market, "start_time": start_time, "end_time": end_time},
        )

    async def m_wallet_limits(self) -> dict[str, str]:
        payload = await self.endpoint.raw(M_WALLET_LIMITS)
        return cast("dict[str, str]", payload)

    async def m_wallet_interest_rates(self) -> dict[str, InterestRate]:
        return await self.endpoint.model_mapping(M_WALLET_INTEREST_RATES, InterestRate)

    async def create_m_wallet_loan(self, *, currency: str, amount: str) -> MWalletLoan:
        return await self.endpoint.model(CREATE_M_WALLET_LOAN, MWalletLoan, {"currency": currency, "amount": amount})

    async def m_wallet_loans(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletLoan]:
        return await self.endpoint.model_list(
            M_WALLET_LOANS,
            MWalletLoan,
            {"currency": currency, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def create_m_wallet_transfer(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
        return await self.endpoint.model(
            CREATE_M_WALLET_TRANSFER,
            MWalletTransfer,
            {"currency": currency, "amount": amount, "side": side},
        )

    async def m_wallet_transfers(
        self,
        *,
        currency: str,
        side: str,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletTransfer]:
        return await self.endpoint.model_list(
            M_WALLET_TRANSFERS,
            MWalletTransfer,
            {"currency": currency, "side": side, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def create_m_wallet_repayment(self, *, currency: str, amount: str) -> MWalletRepayment:
        return await self.endpoint.model(
            CREATE_M_WALLET_REPAYMENT,
            MWalletRepayment,
            {"currency": currency, "amount": amount},
        )

    async def m_wallet_repayments(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletRepayment]:
        return await self.endpoint.model_list(
            M_WALLET_REPAYMENTS,
            MWalletRepayment,
            {"currency": currency, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def m_wallet_liquidations(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLiquidation]:
        return await self.endpoint.model_list(
            M_WALLET_LIQUIDATIONS,
            MWalletLiquidation,
            {"timestamp": timestamp, "order": order, "limit": limit},
        )

    async def m_wallet_liquidation(self, sn: str) -> MWalletLiquidationDetail:
        return await self.endpoint.model(M_WALLET_LIQUIDATION, MWalletLiquidationDetail, {"sn": sn})

    async def m_wallet_interests(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletInterest]:
        return await self.endpoint.model_list(
            M_WALLET_INTERESTS,
            MWalletInterest,
            {"currency": currency, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def m_wallet_ad_ratio(self) -> MWalletADRatio:
        return await self.endpoint.model(M_WALLET_AD_RATIO, MWalletADRatio)
