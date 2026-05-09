from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass

from maicoin.ws._stream.lifecycle import call_lifecycle
from maicoin.ws._stream.types import ConnectFactory
from maicoin.ws._stream.types import LifecycleCallback
from maicoin.ws._stream.types import WebSocketConnection

Sleep = Callable[[float], Awaitable[object]]
ConnectedRun = Callable[[WebSocketConnection], Awaitable[object]]


@dataclass(frozen=True)
class ReconnectPolicy:
    """Reconnect/backoff configuration for [`Stream`][maicoin.ws.Stream].

    Args:
        enabled: Whether to reconnect after non-cancellation disconnects.
        max_retries: Maximum reconnect attempts after the initial connection.
            `None` retries forever.
        base_delay: Initial backoff delay in seconds.
        max_delay: Maximum backoff delay in seconds.
        jitter: Random delay added to each backoff, in seconds.
    """

    enabled: bool = True
    max_retries: int | None = None
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: float = 1.0

    def delay(self, retry_number: int) -> float:
        """Return the reconnect delay for a 1-based retry number."""
        backoff = min(self.max_delay, self.base_delay * 2 ** max(0, retry_number - 1))
        if self.jitter <= 0:
            return backoff
        return backoff + random.uniform(0, self.jitter)


def should_reconnect(policy: ReconnectPolicy, retry_count: int) -> bool:
    if not policy.enabled:
        return False
    return policy.max_retries is None or retry_count <= policy.max_retries


class ReconnectLoop:
    """Own reconnect retry state, lifecycle callback ordering, and backoff sleep."""

    def __init__(
        self,
        *,
        uri: str,
        connect_factory: ConnectFactory,
        connect_options: dict[str, object],
        reconnect_policy: ReconnectPolicy,
        run_connected: ConnectedRun,
        on_disconnected: LifecycleCallback | None = None,
        on_reconnecting: LifecycleCallback | None = None,
        on_permanent_failure: LifecycleCallback | None = None,
        sleep: Sleep = asyncio.sleep,
    ) -> None:
        self.uri = uri
        self.connect_factory = connect_factory
        self.connect_options = connect_options
        self.reconnect_policy = reconnect_policy
        self.run_connected = run_connected
        self.on_disconnected = on_disconnected
        self.on_reconnecting = on_reconnecting
        self.on_permanent_failure = on_permanent_failure
        self.sleep = sleep

    async def run(self) -> None:
        retry_count = 0
        while True:
            try:
                async with self.connect_factory(self.uri, **self.connect_options) as ws:
                    retry_count = 0
                    await self.run_connected(ws)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await call_lifecycle(self.on_disconnected, exc)
                retry_count += 1
                if not self.should_reconnect(retry_count):
                    await call_lifecycle(self.on_permanent_failure, exc)
                    raise
                await call_lifecycle(self.on_reconnecting, exc)
                delay = self.reconnect_policy.delay(retry_count)
                if delay > 0:
                    await self.sleep(delay)

    def should_reconnect(self, retry_count: int) -> bool:
        return should_reconnect(self.reconnect_policy, retry_count)
