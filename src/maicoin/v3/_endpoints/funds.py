"""Funds, deposits, withdrawals, and settlement REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3.models.funds import Deposit
from maicoin.v3.models.funds import DepositAddress
from maicoin.v3.models.funds import FundTransactionDeposit
from maicoin.v3.models.funds import FundTransactionTransfer
from maicoin.v3.models.funds import FundTransactionWithdrawal
from maicoin.v3.models.funds import InternalTransfer
from maicoin.v3.models.funds import Reward
from maicoin.v3.models.funds import WithdrawAddress
from maicoin.v3.models.funds import Withdrawal

WITHDRAWAL = EndpointSpec("GET", "/api/v3/withdrawal", auth=True)
CREATE_WITHDRAWAL = EndpointSpec("POST", "/api/v3/withdrawal", auth=True)
CREATE_TWD_WITHDRAWAL = EndpointSpec("POST", "/api/v3/withdrawal/twd", auth=True)
WITHDRAWALS = EndpointSpec("GET", "/api/v3/withdrawals", auth=True)
WITHDRAW_ADDRESSES = EndpointSpec("GET", "/api/v3/withdraw_addresses", auth=True)
DEPOSIT = EndpointSpec("GET", "/api/v3/deposit", auth=True)
DEPOSITS = EndpointSpec("GET", "/api/v3/deposits", auth=True)
DEPOSIT_ADDRESS = EndpointSpec("GET", "/api/v3/deposit_address", auth=True)
INTERNAL_TRANSFERS = EndpointSpec("GET", "/api/v3/internal_transfers", auth=True)
REWARDS = EndpointSpec("GET", "/api/v3/rewards", auth=True)
FUND_TRANSACTION_DEPOSITS = EndpointSpec("GET", "/api/v3/fund_transactions/deposits", auth=True)
FUND_TRANSACTION_DEPOSIT = EndpointSpec("GET", "/api/v3/fund_transactions/deposit", auth=True)
FUND_TRANSACTION_WITHDRAWALS = EndpointSpec("GET", "/api/v3/fund_transactions/withdrawals", auth=True)
FUND_TRANSACTION_WITHDRAWAL = EndpointSpec("GET", "/api/v3/fund_transactions/withdrawal", auth=True)
FUND_TRANSACTION_TRANSFERS = EndpointSpec("GET", "/api/v3/fund_transactions/transfers", auth=True)
FUND_TRANSACTION_TRANSFER = EndpointSpec("GET", "/api/v3/fund_transactions/transfer", auth=True)


@dataclass(frozen=True, slots=True)
class FundsEndpoints:
    """Authenticated fund movement request/parse rules."""

    requester: RestRequester

    @property
    def endpoint(self) -> EndpointExecutor:
        return EndpointExecutor(self.requester)

    async def withdrawal(self, uuid: str) -> Withdrawal:
        return await self.endpoint.model(WITHDRAWAL, Withdrawal, {"uuid": uuid})

    async def create_withdrawal(self, *, withdraw_address_uuid: str, amount: str) -> Withdrawal:
        return await self.endpoint.model(
            CREATE_WITHDRAWAL,
            Withdrawal,
            {"withdraw_address_uuid": withdraw_address_uuid, "amount": amount},
        )

    async def create_twd_withdrawal(self, amount: str) -> Withdrawal:
        return await self.endpoint.model(CREATE_TWD_WITHDRAWAL, Withdrawal, {"amount": amount})

    async def withdrawals(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Withdrawal]:
        return await self.endpoint.model_list(
            WITHDRAWALS,
            Withdrawal,
            {"currency": currency, "state": state, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def withdraw_addresses(
        self,
        currency: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[WithdrawAddress]:
        return await self.endpoint.model_list(
            WITHDRAW_ADDRESSES,
            WithdrawAddress,
            {"currency": currency, "limit": limit, "offset": offset},
        )

    async def deposit(self, *, txid: str | None = None, uuid: str | None = None) -> Deposit:
        return await self.endpoint.model(DEPOSIT, Deposit, {"txid": txid, "uuid": uuid})

    async def deposits(
        self,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[Deposit]:
        return await self.endpoint.model_list(
            DEPOSITS,
            Deposit,
            {"currency": currency, "timestamp": timestamp, "order": order, "limit": limit},
        )

    async def deposit_address(self, currency_version: str) -> DepositAddress:
        return await self.endpoint.model(DEPOSIT_ADDRESS, DepositAddress, {"currency_version": currency_version})

    async def internal_transfers(
        self,
        side: str,
        *,
        currency: str | None = None,
        timestamp: int | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[InternalTransfer]:
        return await self.endpoint.model_list(
            INTERNAL_TRANSFERS,
            InternalTransfer,
            {"side": side, "currency": currency, "timestamp": timestamp, "order": order, "limit": limit},
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
        return await self.endpoint.model_list(
            REWARDS,
            Reward,
            {
                "reward_type": reward_type,
                "currency": currency,
                "timestamp": timestamp,
                "order": order,
                "limit": limit,
            },
        )

    async def fund_transaction_deposits(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionDeposit]:
        return await self.endpoint.model_list(
            FUND_TRANSACTION_DEPOSITS,
            FundTransactionDeposit,
            {"timestamp": timestamp, "order": order, "limit": limit},
        )

    async def fund_transaction_deposit(self, sn: str) -> FundTransactionDeposit:
        return await self.endpoint.model(FUND_TRANSACTION_DEPOSIT, FundTransactionDeposit, {"sn": sn})

    async def fund_transaction_withdrawals(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionWithdrawal]:
        return await self.endpoint.model_list(
            FUND_TRANSACTION_WITHDRAWALS,
            FundTransactionWithdrawal,
            {"timestamp": timestamp, "order": order, "limit": limit},
        )

    async def fund_transaction_withdrawal(self, sn: str) -> FundTransactionWithdrawal:
        return await self.endpoint.model(FUND_TRANSACTION_WITHDRAWAL, FundTransactionWithdrawal, {"sn": sn})

    async def fund_transaction_transfers(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[FundTransactionTransfer]:
        return await self.endpoint.model_list(
            FUND_TRANSACTION_TRANSFERS,
            FundTransactionTransfer,
            {"timestamp": timestamp, "order": order, "limit": limit},
        )

    async def fund_transaction_transfer(self, sn: str) -> FundTransactionTransfer:
        return await self.endpoint.model(FUND_TRANSACTION_TRANSFER, FundTransactionTransfer, {"sn": sn})
