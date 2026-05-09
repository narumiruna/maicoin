from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Literal
from typing import Protocol

from maicoin.ws.response import Response

DispatchMode = Literal["inline", "task", "queue"]
"""Response dispatch strategy used by [`Stream`][maicoin.ws.Stream]."""

Handler = Callable[[Response], object | Awaitable[object]]
LifecycleCallback = Callable[[Exception | None], object | Awaitable[object]]
HandlerErrorCallback = Callable[[Exception, Response], object | Awaitable[object]]


class WebSocketConnection(Protocol):
    """Minimal async websocket connection protocol used by [`Stream`][maicoin.ws.Stream]."""

    async def send(self, message: str) -> None: ...

    async def recv(self) -> str | bytes: ...

    async def close(self) -> None: ...


class WebSocketContext(Protocol):
    """Async context manager returned by websocket connect factories."""

    async def __aenter__(self) -> WebSocketConnection: ...

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None: ...


ConnectFactory = Callable[..., WebSocketContext]
