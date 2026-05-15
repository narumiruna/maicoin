from __future__ import annotations

import os

import pytest

from maicoin.v3 import Client


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    live_enabled = os.environ.get("RUN_LIVE_TESTS") == "1"
    destructive_enabled = os.environ.get("RUN_DESTRUCTIVE_TESTS") == "1"
    skip_live = pytest.mark.skip(reason="set RUN_LIVE_TESTS=1 to run live integration tests")
    skip_destructive = pytest.mark.skip(
        reason="set RUN_DESTRUCTIVE_TESTS=1 only after reviewing destructive live-test safety controls"
    )
    for item in items:
        if "live" in item.keywords and not live_enabled:
            item.add_marker(skip_live)
        if "destructive" in item.keywords and not destructive_enabled:
            item.add_marker(skip_destructive)


@pytest.fixture(scope="session")
def live_market() -> str:
    return os.environ.get("MAX_LIVE_MARKET", "btctwd")


@pytest.fixture(scope="session")
def public_client() -> Client:
    return Client()


@pytest.fixture(scope="session")
def private_client() -> Client:
    api_key = os.environ.get("MAX_API_KEY")
    api_secret = os.environ.get("MAX_API_SECRET")
    if api_key is None or api_secret is None:
        pytest.skip("MAX_API_KEY and MAX_API_SECRET are required for private live tests")
    return Client(api_key=api_key, api_secret=api_secret)
