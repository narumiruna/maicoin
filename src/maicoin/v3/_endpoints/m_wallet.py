"""M-Wallet REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import compact
from maicoin.v3.models import HistoricalIndexPrice
from maicoin.v3.models import InterestRate
from maicoin.v3.models import MWalletADRatio
from maicoin.v3.models import MWalletInterest
from maicoin.v3.models import MWalletLiquidation
from maicoin.v3.models import MWalletLiquidationDetail
from maicoin.v3.models import MWalletLoan
from maicoin.v3.models import MWalletRepayment
from maicoin.v3.models import MWalletTransfer


@dataclass(frozen=True, slots=True)
class MWalletEndpoints:
    """M-Wallet public and authenticated request/parse rules."""

    requester: RestRequester

    async def m_wallet_index_prices(self) -> dict[str, str]:
        payload = await self.requester.request("GET", "/api/v3/wallet/m/index_prices")
        return cast("dict[str, str]", payload)

    async def m_wallet_historical_index_prices(
        self,
        market: str,
        *,
        start_time: int,
        end_time: int,
    ) -> list[HistoricalIndexPrice]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/historical_index_prices",
            params={"market": market, "start_time": start_time, "end_time": end_time},
        )
        return [HistoricalIndexPrice.model_validate(item) for item in cast("list[object]", payload)]

    async def m_wallet_limits(self) -> dict[str, str]:
        payload = await self.requester.request("GET", "/api/v3/wallet/m/limits")
        return cast("dict[str, str]", payload)

    async def m_wallet_interest_rates(self) -> dict[str, InterestRate]:
        payload = await self.requester.request("GET", "/api/v3/wallet/m/interest_rates")
        return {
            currency: InterestRate.model_validate(rate) for currency, rate in cast("dict[str, object]", payload).items()
        }

    async def create_m_wallet_loan(self, *, currency: str, amount: str) -> MWalletLoan:
        payload = await self.requester.request(
            "POST",
            "/api/v3/wallet/m/loan",
            params={"currency": currency, "amount": amount},
            auth=True,
        )
        return MWalletLoan.model_validate(payload)

    async def m_wallet_loans(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletLoan]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/loans",
            params=compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLoan.model_validate(item) for item in cast("list[object]", payload)]

    async def create_m_wallet_transfer(self, *, currency: str, amount: str, side: str) -> MWalletTransfer:
        payload = await self.requester.request(
            "POST",
            "/api/v3/wallet/m/transfer",
            params={"currency": currency, "amount": amount, "side": side},
            auth=True,
        )
        return MWalletTransfer.model_validate(payload)

    async def m_wallet_transfers(
        self,
        *,
        currency: str,
        side: str,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletTransfer]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/transfers",
            params=compact(
                {"currency": currency, "side": side, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [MWalletTransfer.model_validate(item) for item in cast("list[object]", payload)]

    async def create_m_wallet_repayment(self, *, currency: str, amount: str) -> MWalletRepayment:
        payload = await self.requester.request(
            "POST",
            "/api/v3/wallet/m/repayment",
            params={"currency": currency, "amount": amount},
            auth=True,
        )
        return MWalletRepayment.model_validate(payload)

    async def m_wallet_repayments(
        self,
        currency: str,
        *,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletRepayment]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/repayments",
            params=compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletRepayment.model_validate(item) for item in cast("list[object]", payload)]

    async def m_wallet_liquidations(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[MWalletLiquidation]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/liquidations",
            params=compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletLiquidation.model_validate(item) for item in cast("list[object]", payload)]

    async def m_wallet_liquidation(self, sn: str) -> MWalletLiquidationDetail:
        payload = await self.requester.request("GET", "/api/v3/wallet/m/liquidation", params={"sn": sn}, auth=True)
        return MWalletLiquidationDetail.model_validate(payload)

    async def m_wallet_interests(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[MWalletInterest]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/wallet/m/interests",
            params=compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [MWalletInterest.model_validate(item) for item in cast("list[object]", payload)]

    async def m_wallet_ad_ratio(self) -> MWalletADRatio:
        payload = await self.requester.request("GET", "/api/v3/wallet/m/ad_ratio", auth=True)
        return MWalletADRatio.model_validate(payload)
