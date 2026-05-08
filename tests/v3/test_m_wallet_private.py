from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import cast

from maicoin.v3 import Client
from maicoin.v3 import MWalletADRatio
from maicoin.v3 import MWalletInterest
from maicoin.v3 import MWalletLiquidation
from maicoin.v3 import MWalletLiquidationDetail
from maicoin.v3 import MWalletLoan
from maicoin.v3 import MWalletRepayment
from maicoin.v3 import MWalletTransfer


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.status_code = 200
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, payload: object) -> None:
        self.response = FakeResponse(payload)
        self.calls: list[dict[str, object]] = []

    def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return self.response


def authenticated_client(session: FakeSession) -> Client:
    return Client(
        api_key="key",
        api_secret="secret",
        base_url="https://example.test",
        session=session,
        nonce_factory=lambda: 123456,
    )


def last_kwargs(session: FakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1]["kwargs"])


def last_payload(session: FakeSession) -> Mapping[str, object]:
    headers = cast("Mapping[str, str]", last_kwargs(session)["headers"])
    payload = base64.b64decode(headers["X-MAX-PAYLOAD"]).decode()
    return cast("Mapping[str, object]", json.loads(payload))


def loan_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "210407080800050666",
        "currency": "eth",
        "amount": "0.019",
        "state": "confirmed",
        "created_at": 1521726960357,
        "interest_rate": "0.001",
    }
    payload.update(overrides)
    return payload


def transfer_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "210407080800050666",
        "side": "in",
        "currency": "eth",
        "amount": "0.019",
        "created_at": 1521726960123,
        "state": "processing",
    }
    payload.update(overrides)
    return payload


def repayment_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "currency": "eth",
        "amount": "0.15",
        "principal": "0.1",
        "interest": "0.05",
        "state": "confirmed",
        "sn": "210407080800050666",
        "created_at": 1521726960123,
    }
    payload.update(overrides)
    return payload


def liquidation_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "sn": "210407080800050666",
        "ad_ratio": "1.2",
        "expected_ad_ratio": "1.5",
        "created_at": 1521726960357,
        "state": "liquidated",
    }
    payload.update(overrides)
    return payload


def liquidation_detail_payload() -> dict[str, object]:
    repayment = {
        "currency": "eth",
        "amount": "0.15",
        "principal": "0.1",
        "interest": "0.05",
        "state": "confirmed",
    }
    return liquidation_payload(
        repayments=[repayment],
        liquidations=[
            {
                "market": "ethusdt",
                "type": "buy",
                "price": "3200",
                "volume": "0.1",
                "fee": "0.001",
                "fee_currency": "eth",
                "repayment": repayment,
            }
        ],
    )


def test_create_m_wallet_loan_and_history_construct_authenticated_requests() -> None:
    create_session = FakeSession(loan_payload())
    loan = authenticated_client(create_session).create_m_wallet_loan(currency="eth", amount="0.019")

    assert loan == MWalletLoan.model_validate(loan_payload())
    assert create_session.calls[-1]["method"] == "POST"
    assert create_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/loan"
    assert last_kwargs(create_session)["json"] == {"nonce": 123456, "currency": "eth", "amount": "0.019"}
    assert last_payload(create_session)["path"] == "/api/v3/wallet/m/loan"

    list_session = FakeSession([loan_payload()])
    loans = authenticated_client(list_session).m_wallet_loans("eth", timestamp=1521726960357, order="desc", limit=1)
    assert loans == [MWalletLoan.model_validate(loan_payload())]
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/loans"
    assert last_kwargs(list_session)["params"] == {
        "nonce": 123456,
        "currency": "eth",
        "timestamp": 1521726960357,
        "order": "desc",
        "limit": 1,
    }


def test_m_wallet_transfer_create_and_history_construct_requests() -> None:
    create_session = FakeSession(transfer_payload())
    transfer = authenticated_client(create_session).create_m_wallet_transfer(currency="eth", amount="0.019", side="in")

    assert transfer == MWalletTransfer.model_validate(transfer_payload())
    assert create_session.calls[-1]["method"] == "POST"
    assert create_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/transfer"
    assert last_kwargs(create_session)["json"] == {"nonce": 123456, "currency": "eth", "amount": "0.019", "side": "in"}

    list_session = FakeSession([transfer_payload()])
    transfers = authenticated_client(list_session).m_wallet_transfers(currency="eth", side="in", limit=1)
    assert transfers == [MWalletTransfer.model_validate(transfer_payload())]
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/transfers"
    assert last_kwargs(list_session)["params"] == {"nonce": 123456, "currency": "eth", "side": "in", "limit": 1}


def test_m_wallet_repayment_create_and_history_construct_requests() -> None:
    create_session = FakeSession(repayment_payload())
    repayment = authenticated_client(create_session).create_m_wallet_repayment(currency="eth", amount="0.15")

    assert repayment == MWalletRepayment.model_validate(repayment_payload())
    assert create_session.calls[-1]["method"] == "POST"
    assert create_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/repayment"
    assert last_kwargs(create_session)["json"] == {"nonce": 123456, "currency": "eth", "amount": "0.15"}

    list_session = FakeSession([repayment_payload()])
    repayments = authenticated_client(list_session).m_wallet_repayments("eth", order="asc", limit=1)
    assert repayments == [MWalletRepayment.model_validate(repayment_payload())]
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/repayments"
    assert last_kwargs(list_session)["params"] == {"nonce": 123456, "currency": "eth", "order": "asc", "limit": 1}


def test_m_wallet_liquidations_and_detail_parse_nested_payloads() -> None:
    list_session = FakeSession([liquidation_payload()])
    liquidations = authenticated_client(list_session).m_wallet_liquidations(limit=1)

    assert liquidations == [MWalletLiquidation.model_validate(liquidation_payload())]
    assert list_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/liquidations"
    assert last_kwargs(list_session)["params"] == {"nonce": 123456, "limit": 1}

    detail_session = FakeSession(liquidation_detail_payload())
    detail = authenticated_client(detail_session).m_wallet_liquidation("210407080800050666")
    assert detail == MWalletLiquidationDetail.model_validate(liquidation_detail_payload())
    assert detail.repayments[0].principal == "0.1"
    assert detail.liquidations[0].repayment.interest == "0.05"
    assert detail_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/liquidation"
    assert last_kwargs(detail_session)["params"] == {"nonce": 123456, "sn": "210407080800050666"}


def test_m_wallet_interests_and_ad_ratio_construct_authenticated_requests() -> None:
    interest_payload = {
        "currency": "eth",
        "amount": "0.003",
        "interest_rate": "0.001",
        "principal": "3",
        "created_at": 1521726960123,
    }
    interests_session = FakeSession([interest_payload])
    interests = authenticated_client(interests_session).m_wallet_interests(currency="eth", limit=1)

    assert interests == [MWalletInterest.model_validate(interest_payload)]
    assert interests_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/interests"
    assert last_kwargs(interests_session)["params"] == {"nonce": 123456, "currency": "eth", "limit": 1}

    ad_ratio_payload = {"ad_ratio": "1.21", "asset_in_usdt": "2639.98128484", "debt_in_usdt": "2165.54482641"}
    ad_ratio_session = FakeSession(ad_ratio_payload)
    ad_ratio = authenticated_client(ad_ratio_session).m_wallet_ad_ratio()
    assert ad_ratio == MWalletADRatio.model_validate(ad_ratio_payload)
    assert ad_ratio_session.calls[-1]["url"] == "https://example.test/api/v3/wallet/m/ad_ratio"
    assert last_payload(ad_ratio_session) == {"nonce": 123456, "path": "/api/v3/wallet/m/ad_ratio"}
