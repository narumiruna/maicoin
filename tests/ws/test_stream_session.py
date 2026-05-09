from __future__ import annotations

import asyncio

import pytest

from maicoin.ws import Channel
from maicoin.ws import Response
from maicoin.ws import Subscription
from maicoin.ws._stream.dispatch import ResponseDispatcher
from maicoin.ws._stream.session import ConnectedSession
from maicoin.ws.request import Request

MESSAGE = '{"e":"subscribed","s":[{"channel":"trade","market":"btctwd"}],"i":"client1","T":123456789}'


class FakeConnection:
    def __init__(self, messages: list[str | BaseException]) -> None:
        self.messages = messages
        self.sent: list[str] = []

    async def send(self, message: str) -> None:
        self.sent.append(message)

    async def recv(self) -> str:
        item = self.messages.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    async def close(self) -> None:
        return None


@pytest.mark.anyio
async def test_connected_session_replays_requests_then_parses_and_dispatches_responses() -> None:
    queue: asyncio.Queue[Response] = asyncio.Queue()
    events: list[str] = []
    connection = FakeConnection([MESSAGE, asyncio.CancelledError()])
    request = Request.subscribe([Subscription(channel=Channel.TRADE, market="btctwd")])
    session = ConnectedSession(
        requests=[request],
        dispatcher=ResponseDispatcher(dispatch="queue", handlers=[], response_queue=queue),
        on_connected=lambda _exc: events.append("connected"),
    )

    with pytest.raises(asyncio.CancelledError):
        await session.run(connection)

    response = queue.get_nowait()
    assert connection.sent == [request.message()]
    assert events == ["connected"]
    assert response.event == "subscribed"
