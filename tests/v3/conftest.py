from __future__ import annotations

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Run AnyIO-marked REST client tests on asyncio only."""
    return "asyncio"
