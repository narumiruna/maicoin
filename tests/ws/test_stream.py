from __future__ import annotations

import asyncio
from collections.abc import Callable
from collections.abc import Iterator

import pytest

from maicoin.ws import Channel
from maicoin.ws import Filter
from maicoin.ws import ReconnectPolicy
from maicoin.ws import Response
from maicoin.ws import Stream
from maicoin.ws import Subscription

MESSAGE = '{"e":"subscribed","s":[{"channel":"trade","market":"btctwd"}],"i":"client1","T":123456789}'


class FakeConnection:
    def __init__(self, messages: list[str | BaseException]) -> None:
        self.messages = messages
        self.sent: list[str] = []
        self.closed = False

    async def send(self, message: str) -> None:
        self.sent.append(message)

    async def recv(self) -> str:
        item = self.messages.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    async def close(self) -> None:
        self.closed = True


class FakeContext:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


def connect_factory(connections: list[FakeConnection]) -> Callable[..., FakeContext]:
    iterator: Iterator[FakeConnection] = iter(connections)

    def connect(*_args: object, **_kwargs: object) -> FakeContext:
        return FakeContext(next(iterator))

    return connect


@pytest.mark.anyio
async def test_stream_reconnects_and_replays_subscriptions() -> None:
    first = FakeConnection([ConnectionError("dropped")])
    second = FakeConnection([MESSAGE, asyncio.CancelledError()])
    seen: list[Response] = []
    events: list[str] = []
    stream = Stream(
        reconnect_policy=ReconnectPolicy(max_retries=1, base_delay=0, jitter=0),
        connect_factory=connect_factory([first, second]),
        on_disconnected=lambda _exc: events.append("disconnected"),
        on_reconnecting=lambda _exc: events.append("reconnecting"),
    )
    stream.subscribe([Subscription(channel=Channel.TRADE, market="btctwd")])
    stream.add_handler(seen.append)

    with pytest.raises(asyncio.CancelledError):
        await stream.arun()

    assert len(first.sent) == 1
    assert first.sent == second.sent
    assert [response.event for response in seen] == ["subscribed"]
    assert events == ["disconnected", "reconnecting"]


@pytest.mark.anyio
async def test_stream_queue_dispatch_does_not_call_handlers() -> None:
    connection = FakeConnection([MESSAGE, asyncio.CancelledError()])
    stream = Stream(
        reconnect=False,
        dispatch="queue",
        connect_factory=connect_factory([connection]),
    )

    def fail_handler(_response: Response) -> None:
        raise AssertionError("queue dispatch should not call registered handlers")

    stream.add_handler(fail_handler)

    with pytest.raises(asyncio.CancelledError):
        await stream.arun()

    response = stream.response_queue.get_nowait()
    assert response.event == "subscribed"


@pytest.mark.anyio
async def test_stream_task_dispatch_reports_handler_errors_without_stopping_receive_loop() -> None:
    connection = FakeConnection([MESSAGE, MESSAGE, ConnectionError("closed")])
    errors: list[tuple[Exception, Response]] = []
    seen: list[str] = []

    async def bad_handler(response: Response) -> None:
        seen.append(response.event)
        raise RuntimeError("boom")

    stream = Stream(
        reconnect=False,
        dispatch="task",
        connect_factory=connect_factory([connection]),
        on_handler_error=lambda exc, response: errors.append((exc, response)),
    )
    stream.add_handler(bad_handler)

    with pytest.raises(ConnectionError):
        await stream.arun()

    await asyncio.sleep(0)
    assert seen == ["subscribed", "subscribed"]
    assert [response.event for _exc, response in errors] == ["subscribed", "subscribed"]


def test_stream_forwards_websocket_connect_options() -> None:
    captured: dict[str, object] = {}

    def connect(*args: object, **kwargs: object) -> FakeContext:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeContext(FakeConnection([asyncio.CancelledError()]))

    stream = Stream(
        uri="wss://example.invalid/ws",
        reconnect=False,
        connect_factory=connect,
        ping_interval=10,
        ping_timeout=5,
        close_timeout=2,
        max_queue=16,
    )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(stream.arun())

    assert captured == {
        "args": ("wss://example.invalid/ws",),
        "kwargs": {"ping_interval": 10, "ping_timeout": 5, "close_timeout": 2, "max_queue": 16},
    }


def test_stream_auth_can_request_private_filters() -> None:
    stream = Stream(api_key="key", api_secret="secret", auth_filters=[Filter.ORDER, Filter.FAST_TRADE_UPDATE])

    assert stream.requests[0].filters == [Filter.ORDER, Filter.FAST_TRADE_UPDATE]
