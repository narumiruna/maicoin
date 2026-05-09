from __future__ import annotations

import maicoin.v3 as v3
from maicoin.v3 import models
from maicoin.v3.models import ConvertOrder
from maicoin.v3.models import Market
from maicoin.v3.models import MWalletLoan
from maicoin.v3.models import Order
from maicoin.v3.models import Withdrawal
from maicoin.v3.models.convert import ConvertOrder as DomainConvertOrder
from maicoin.v3.models.funds import Withdrawal as DomainWithdrawal
from maicoin.v3.models.m_wallet import MWalletLoan as DomainMWalletLoan
from maicoin.v3.models.orders import Order as DomainOrder
from maicoin.v3.models.public_market_data import Market as DomainMarket


def test_v3_model_reexports_preserve_public_imports() -> None:
    assert v3.Market is Market
    assert v3.Order is Order
    assert v3.Withdrawal is Withdrawal
    assert v3.ConvertOrder is ConvertOrder
    assert v3.MWalletLoan is MWalletLoan


def test_v3_model_domain_modules_export_same_classes() -> None:
    assert models.Market is DomainMarket
    assert models.Order is DomainOrder
    assert models.Withdrawal is DomainWithdrawal
    assert models.ConvertOrder is DomainConvertOrder
    assert models.MWalletLoan is DomainMWalletLoan
