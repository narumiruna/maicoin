from __future__ import annotations

import pytest

from maicoin.v3 import Client

pytestmark = pytest.mark.live


def test_info(private_client: Client) -> None:
    info = private_client.info_sync()

    assert info.email
    assert info.level >= 0
    assert info.current_vip_level.level >= 0


def test_accounts(private_client: Client) -> None:
    accounts = private_client.accounts_sync()

    assert accounts
    assert all(account.currency for account in accounts)


def test_open_orders(private_client: Client) -> None:
    orders = private_client.open_orders_sync(limit=1)

    assert len(orders) <= 1
    for order in orders:
        assert order.id > 0
        assert order.wallet_type == "spot"


def test_closed_orders(private_client: Client) -> None:
    orders = private_client.closed_orders_sync(limit=1)

    assert len(orders) <= 1
    for order in orders:
        assert order.id > 0
        assert order.wallet_type == "spot"


def test_wallet_trades(private_client: Client) -> None:
    trades = private_client.wallet_trades_sync(limit=1)

    assert len(trades) <= 1
    for trade in trades:
        assert trade.id > 0
        assert trade.wallet_type == "spot"
