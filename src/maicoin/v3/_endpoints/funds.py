"""Funds, deposits, withdrawals, and settlement REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import compact
from maicoin.v3.models import Deposit
from maicoin.v3.models import DepositAddress
from maicoin.v3.models import FundTransactionDeposit
from maicoin.v3.models import FundTransactionTransfer
from maicoin.v3.models import FundTransactionWithdrawal
from maicoin.v3.models import InternalTransfer
from maicoin.v3.models import Reward
from maicoin.v3.models import WithdrawAddress
from maicoin.v3.models import Withdrawal


@dataclass(frozen=True, slots=True)
class FundsEndpoints:
    """Authenticated fund movement request/parse rules."""

    requester: RestRequester

    async def withdrawal(self, uuid: str) -> Withdrawal:
        payload = await self.requester.request("GET", "/api/v3/withdrawal", params={"uuid": uuid}, auth=True)
        return Withdrawal.model_validate(payload)

    async def create_withdrawal(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        payload = await self.requester.request(
            "POST",
            "/api/v3/withdrawal",
            params={"withdraw_address_uuid": withdraw_address_uuid, "amount": amount},
            auth=True,
        )
        return Withdrawal.model_validate(payload)

    async def create_twd_withdrawal(self, amount: str) -> Withdrawal:
        payload = await self.requester.request("POST", "/api/v3/withdrawal/twd", params={"amount": amount}, auth=True)
        return Withdrawal.model_validate(payload)

    async def withdrawals(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Withdrawal]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/withdrawals",
            params=compact(
                {"currency": currency, "state": state, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [Withdrawal.model_validate(item) for item in cast("list[object]", payload)]

    async def withdraw_addresses(
        self,
        currency: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WithdrawAddress]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/withdraw_addresses",
            params=compact({"currency": currency, "limit": limit, "offset": offset}),
            auth=True,
        )
        return [WithdrawAddress.model_validate(item) for item in cast("list[object]", payload)]

    async def deposit(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
        payload = await self.requester.request(
            "GET", "/api/v3/deposit", params=compact({"txid": txid, "uuid": uuid}), auth=True
        )
        return Deposit.model_validate(payload)

    async def deposits(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Deposit]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/deposits",
            params=compact({"currency": currency, "timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [Deposit.model_validate(item) for item in cast("list[object]", payload)]

    async def deposit_address(self, currency_version: str) -> DepositAddress:
        payload = await self.requester.request(
            "GET",
            "/api/v3/deposit_address",
            params={"currency_version": currency_version},
            auth=True,
        )
        return DepositAddress.model_validate(payload)

    async def internal_transfers(
        self,
        side: str,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[InternalTransfer]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/internal_transfers",
            params=compact(
                {"side": side, "currency": currency, "timestamp": timestamp, "order": order, "limit": limit}
            ),
            auth=True,
        )
        return [InternalTransfer.model_validate(item) for item in cast("list[object]", payload)]

    async def rewards(
        self,
        *,
        reward_type: str | None = None,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Reward]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/rewards",
            params=compact(
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

    async def fund_transaction_deposits(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionDeposit]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/fund_transactions/deposits",
            params=compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionDeposit.model_validate(item) for item in cast("list[object]", payload)]

    async def fund_transaction_deposit(self, sn: str) -> FundTransactionDeposit:
        payload = await self.requester.request("GET", "/api/v3/fund_transactions/deposit", params={"sn": sn}, auth=True)
        return FundTransactionDeposit.model_validate(payload)

    async def fund_transaction_withdrawals(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/fund_transactions/withdrawals",
            params=compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionWithdrawal.model_validate(item) for item in cast("list[object]", payload)]

    async def fund_transaction_withdrawal(self, sn: str) -> FundTransactionWithdrawal:
        payload = await self.requester.request(
            "GET", "/api/v3/fund_transactions/withdrawal", params={"sn": sn}, auth=True
        )
        return FundTransactionWithdrawal.model_validate(payload)

    async def fund_transaction_transfers(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/fund_transactions/transfers",
            params=compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [FundTransactionTransfer.model_validate(item) for item in cast("list[object]", payload)]

    async def fund_transaction_transfer(self, sn: str) -> FundTransactionTransfer:
        payload = await self.requester.request(
            "GET", "/api/v3/fund_transactions/transfer", params={"sn": sn}, auth=True
        )
        return FundTransactionTransfer.model_validate(payload)
