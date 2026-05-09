from __future__ import annotations

import pytest

from maicoin.v3 import Deposit
from maicoin.v3 import DepositAddress
from maicoin.v3 import FundTransactionDeposit
from maicoin.v3 import FundTransactionTransfer
from maicoin.v3 import FundTransactionWithdrawal
from maicoin.v3 import InternalTransfer
from maicoin.v3 import Reward
from maicoin.v3 import WithdrawAddress
from maicoin.v3 import Withdrawal
from tests.v3.helpers import FakeSession
from tests.v3.helpers import authenticated_client
from tests.v3.helpers import last_json
from tests.v3.helpers import last_kwargs
from tests.v3.helpers import last_payload

pytestmark = pytest.mark.anyio


def withdrawal_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "uuid": "18022603540001",
        "currency": "usdt",
        "network_protocol": "tron-trc20",
        "amount": "0.019",
        "fee": "0.0",
        "fee_currency": "usdt",
        "to_address": "TU91BoeyrqW9MKaiRPDiE6z7UecK2n2Hze",
        "label": "My Web3 Wallet",
        "txid": None,
        "created_at": 1521726960357,
        "state": "processing",
        "transaction_type": "external",
    }
    payload.update(overrides)
    return payload


def deposit_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "uuid": "18022603540001",
        "currency": "usdt",
        "network_protocol": "ethereum-erc20",
        "amount": "0.019",
        "to_address": "0x5c7d23d516f120d322fc7b116386b7e491739138",
        "txid": "0x8daa98e07886985bd6a142cd81b83582d6085f7eb931dc4984c18c84f2a845e0",
        "created_at": 1521726960357,
        "confirmations": 64,
        "state": "done",
        "state_reason": "",
    }
    payload.update(overrides)
    return payload


def fund_deposit_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "18022603540001",
        "is_internal": False,
        "currency": "usdt",
        "amount": "0.019",
        "state": "done",
        "created_at": 1521726960123,
        "network_protocol": "ethereum-erc20",
        "to_address": "0x5c7d23d516f120d322fc7b116386b7e491739138",
        "txid": "0x8daa98e07886985bd6a142cd81b83582d6085f7eb931dc4984c18c84f2a845e0",
        "from": None,
    }
    payload.update(overrides)
    return payload


def fund_withdrawal_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "18022603540001",
        "is_internal": False,
        "currency": "usdt",
        "amount": "0.019",
        "state": "processing",
        "created_at": 1521726960123,
        "network_protocol": "tron-trc20",
        "fee": "0.0",
        "fee_currency": "usdt",
        "to_address": "TU91BoeyrqW9MKaiRPDiE6z7UecK2n2Hze",
        "label": "My Web3 Wallet",
        "txid": None,
        "to": None,
    }
    payload.update(overrides)
    return payload


def fund_transfer_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "18022603540001",
        "currency": "usdt",
        "amount": "0.019",
        "state": "done",
        "created_at": 1521726960123,
        "from": {"platform": "max", "sn": "src-1", "wallet_type": "spot"},
        "to": {"platform": "max", "sn": "dst-1", "wallet_type": "m"},
    }
    payload.update(overrides)
    return payload


async def test_withdrawal_methods_construct_authenticated_requests_and_parse_payloads() -> None:
    detail_session = FakeSession(withdrawal_payload())
    withdrawal = await authenticated_client(detail_session).withdrawal("18022603540001")

    assert withdrawal == Withdrawal.model_validate(withdrawal_payload())
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/withdrawal"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "uuid": "18022603540001"}

    create_session = FakeSession(withdrawal_payload())
    await authenticated_client(create_session).create_withdrawal(withdraw_address_uuid="addr-1", amount="0.019")
    assert create_session.calls[-1]["method"] == "POST"
    assert last_json(create_session) == {
        "nonce": 123456,
        "withdraw_address_uuid": "addr-1",
        "amount": "0.019",
    }
    assert last_payload(create_session)["path"] == "/api/v3/withdrawal"

    twd_session = FakeSession(withdrawal_payload(currency="twd", network_protocol=None, amount="100"))
    await authenticated_client(twd_session).create_twd_withdrawal("100")
    assert twd_session.calls[-1]["url"] == "https://example.test/api/v3/withdrawal/twd"
    assert last_json(twd_session) == {"nonce": 123456, "amount": "100"}


async def test_withdrawals_and_withdraw_addresses_parse_lists() -> None:
    withdrawals_session = FakeSession([withdrawal_payload()])
    withdrawals = await authenticated_client(withdrawals_session).withdrawals(currency="usdt", state="done", limit=1)

    assert withdrawals == [Withdrawal.model_validate(withdrawal_payload())]
    assert withdrawals_session.calls[-1]["url"] == "https://example.test/api/v3/withdrawals"
    assert last_kwargs(withdrawals_session)["params"] == {
        "nonce": 123456,
        "currency": "usdt",
        "state": "done",
        "limit": 1,
    }

    address_payload = {
        "uuid": "508c9af6-ccc1-4122-b38f-a407e3bac96c",
        "currency": "usdt",
        "network_protocol": "tron-trc20",
        "address": "TU91BoeyrqW9MKaiRPDiE6z7UecK2n2Hze",
        "extra_label": "My Max Wallet",
        "created_at": 1521726960357,
        "activated_at": None,
        "is_internal": True,
        "network_congested": False,
    }
    address_session = FakeSession([address_payload])
    addresses = await authenticated_client(address_session).withdraw_addresses("usdt", limit=10, offset=20)

    assert addresses == [WithdrawAddress.model_validate(address_payload)]
    assert address_session.calls[-1]["url"] == "https://example.test/api/v3/withdraw_addresses"
    assert last_kwargs(address_session)["params"] == {"nonce": 123456, "currency": "usdt", "limit": 10, "offset": 20}


async def test_deposit_methods_construct_authenticated_requests_and_parse_payloads() -> None:
    detail_session = FakeSession(deposit_payload())
    deposit = await authenticated_client(detail_session).deposit(uuid="18022603540001")

    assert deposit == Deposit.model_validate(deposit_payload())
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/deposit"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "uuid": "18022603540001"}

    deposits_session = FakeSession([deposit_payload()])
    deposits = await authenticated_client(deposits_session).deposits(currency="usdt", order="asc", limit=1)
    assert deposits == [Deposit.model_validate(deposit_payload())]
    assert last_kwargs(deposits_session)["params"] == {"nonce": 123456, "currency": "usdt", "order": "asc", "limit": 1}

    address_payload = {
        "currency": "usdt",
        "network_protocol": "tron-trc20",
        "currency_version": "trc20usdt",
        "address": "TU91BoeyrqW9MKaiRPDiE6z7UecK2n2Hze",
    }
    address_session = FakeSession(address_payload)
    address = await authenticated_client(address_session).deposit_address("trc20usdt")
    assert address == DepositAddress.model_validate(address_payload)
    assert address_session.calls[-1]["url"] == "https://example.test/api/v3/deposit_address"
    assert last_kwargs(address_session)["params"] == {"nonce": 123456, "currency_version": "trc20usdt"}


async def test_internal_transfers_and_rewards_construct_requests_and_parse_payloads() -> None:
    transfer_payload = {
        "uuid": "18032011380001",
        "currency": "eth",
        "amount": "0.019",
        "created_at": 1521726960357,
        "from": "pr***@***.com",
        "to": "member@maicoin.com",
        "state": "done",
    }
    transfer_session = FakeSession([transfer_payload])
    transfers = await authenticated_client(transfer_session).internal_transfers("in", currency="eth", limit=1)

    assert transfers == [InternalTransfer.model_validate(transfer_payload)]
    assert transfers[0].from_ == "pr***@***.com"
    assert last_kwargs(transfer_session)["params"] == {"nonce": 123456, "side": "in", "currency": "eth", "limit": 1}

    reward_payload = {
        "uuid": "18032011380001",
        "currency": "eth",
        "amount": "0.019",
        "created_at": 1521726960357,
        "type": "airdrop_reward",
        "note": "2018-11-13 Holding Reward",
    }
    reward_session = FakeSession([reward_payload])
    rewards = await authenticated_client(reward_session).rewards(reward_type="airdrop_reward", limit=1)

    assert rewards == [Reward.model_validate(reward_payload)]
    assert reward_session.calls[-1]["url"] == "https://example.test/api/v3/rewards"
    assert last_kwargs(reward_session)["params"] == {"nonce": 123456, "reward_type": "airdrop_reward", "limit": 1}


async def test_fund_transaction_deposit_methods_parse_list_and_detail() -> None:
    list_session = FakeSession([fund_deposit_payload()])
    deposits = await authenticated_client(list_session).fund_transaction_deposits(
        timestamp=1521726960123, order="desc", limit=1
    )

    assert deposits == [FundTransactionDeposit.model_validate(fund_deposit_payload())]
    assert deposits[0].from_ is None
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/deposits"
    assert last_kwargs(list_session)["params"] == {
        "nonce": 123456,
        "timestamp": 1521726960123,
        "order": "desc",
        "limit": 1,
    }

    detail_session = FakeSession(fund_deposit_payload())
    detail = await authenticated_client(detail_session).fund_transaction_deposit("18022603540001")
    assert detail.sn == "18022603540001"
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/deposit"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "sn": "18022603540001"}


async def test_fund_transaction_withdrawal_methods_parse_list_and_detail() -> None:
    list_session = FakeSession([fund_withdrawal_payload()])
    withdrawals = await authenticated_client(list_session).fund_transaction_withdrawals(limit=1)

    assert withdrawals == [FundTransactionWithdrawal.model_validate(fund_withdrawal_payload())]
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/withdrawals"
    assert last_kwargs(list_session)["params"] == {"nonce": 123456, "limit": 1}

    detail_session = FakeSession(fund_withdrawal_payload())
    withdrawal = await authenticated_client(detail_session).fund_transaction_withdrawal("18022603540001")
    assert withdrawal.sn == "18022603540001"
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/withdrawal"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "sn": "18022603540001"}


async def test_fund_transaction_transfer_methods_parse_list_and_detail() -> None:
    list_session = FakeSession([fund_transfer_payload()])
    transfers = await authenticated_client(list_session).fund_transaction_transfers(limit=1)

    assert transfers == [FundTransactionTransfer.model_validate(fund_transfer_payload())]
    assert transfers[0].from_.wallet_type == "spot"
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/transfers"
    assert last_kwargs(list_session)["params"] == {"nonce": 123456, "limit": 1}

    detail_session = FakeSession(fund_transfer_payload())
    detail = await authenticated_client(detail_session).fund_transaction_transfer("18022603540001")
    assert detail.sn == "18022603540001"
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/fund_transactions/transfer"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "sn": "18022603540001"}
