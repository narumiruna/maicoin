from __future__ import annotations

import asyncio

import pytest

from maicoin.ws._stream.reconnect import ReconnectLoop
from maicoin.ws._stream.reconnect import ReconnectPolicy
from maicoin.ws._stream.types import WebSocketConnection


class FakeConnection:
    async def send(self, message: str) -> None:
        return None

    async def recv(self) -> str:
        raise asyncio.CancelledError

    async def close(self) -> None:
        return None


class FakeContext:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> WebSocketConnection:
        return self.connection

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


def connect_factory(*_args: object, **_kwargs: object) -> FakeContext:
    return FakeContext(FakeConnection())


@pytest.mark.anyio
async def test_reconnect_loop_orders_callbacks_sleep_and_retry() -> None:
    events: list[str] = []
    failures: list[BaseException] = [ConnectionError("dropped"), asyncio.CancelledError()]

    async def run_connected(_connection: WebSocketConnection) -> None:
        events.append("run")
        failure = failures.pop(0)
        raise failure

    async def sleep(delay: float) -> None:
        events.append(f"sleep:{delay}")

    loop = ReconnectLoop(
        uri="wss://example.invalid/ws",
        connect_factory=connect_factory,
        connect_options={},
        reconnect_policy=ReconnectPolicy(max_retries=1, base_delay=0.5, jitter=0),
        run_connected=run_connected,
        on_disconnected=lambda exc: events.append(f"disconnected:{exc}"),
        on_reconnecting=lambda exc: events.append(f"reconnecting:{exc}"),
        sleep=sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await loop.run()

    assert events == ["run", "disconnected:dropped", "reconnecting:dropped", "sleep:0.5", "run"]


@pytest.mark.anyio
async def test_reconnect_loop_calls_permanent_failure_without_retry_when_disabled() -> None:
    events: list[str] = []

    async def run_connected(_connection: WebSocketConnection) -> None:
        events.append("run")
        raise ConnectionError("closed")

    async def sleep(_delay: float) -> None:
        raise AssertionError("disabled reconnect should not sleep")

    loop = ReconnectLoop(
        uri="wss://example.invalid/ws",
        connect_factory=connect_factory,
        connect_options={},
        reconnect_policy=ReconnectPolicy(enabled=False, base_delay=0, jitter=0),
        run_connected=run_connected,
        on_disconnected=lambda exc: events.append(f"disconnected:{exc}"),
        on_reconnecting=lambda exc: events.append(f"reconnecting:{exc}"),
        on_permanent_failure=lambda exc: events.append(f"permanent:{exc}"),
        sleep=sleep,
    )

    with pytest.raises(ConnectionError):
        await loop.run()

    assert events == ["run", "disconnected:closed", "permanent:closed"]
