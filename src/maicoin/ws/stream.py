"""WebSocket stream client for the [MaiCoin MAX WebSocket API](https://maicoin.github.io/max-websocket-docs/).

The client opens a connection, queues subscription/auth requests, and dispatches
incoming messages to registered handlers as typed [`Response`][maicoin.ws.Response]
objects. It can also reconnect with backoff and replay queued requests after a
transient disconnect.
"""

from __future__ import annotations

import asyncio
import inspect
import os
import random
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal
from typing import Protocol
from typing import cast

import websockets

from maicoin.ws.request import Request
from maicoin.ws.response import Response
from maicoin.ws.subscription import Subscription

MAX_WS_URI = os.getenv("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")
"""WebSocket endpoint. Override with the `MAX_WS_URI` env var (e.g. for staging)."""

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


class Stream:
    """Synchronous-style wrapper around the MAX WebSocket connection.

    Build the stream, call [`subscribe`][maicoin.ws.Stream.subscribe] /
    [`add_handler`][maicoin.ws.Stream.add_handler] as many times as you like,
    then call [`run`][maicoin.ws.Stream.run] to block on the event loop.

    Dispatch modes:
        * `inline`: await/call handlers before reading the next websocket message.
        * `task`: schedule handlers with `asyncio.create_task` so slow async
          handlers do not block the receive loop.
        * `queue`: put parsed responses into `response_queue` for consumer-owned
          processing; registered handlers are not invoked.
    """

    requests: list[Request]
    """Pending requests sent in order on every connect (auth first if configured)."""

    handlers: list[Handler]
    """Callbacks invoked with each parsed [`Response`][maicoin.ws.Response]."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        uri: str = MAX_WS_URI,
        reconnect: bool = True,
        reconnect_policy: ReconnectPolicy | None = None,
        dispatch: DispatchMode = "inline",
        response_queue: asyncio.Queue[Response] | None = None,
        connect_factory: ConnectFactory | None = None,
        on_connected: LifecycleCallback | None = None,
        on_disconnected: LifecycleCallback | None = None,
        on_reconnecting: LifecycleCallback | None = None,
        on_permanent_failure: LifecycleCallback | None = None,
        on_handler_error: HandlerErrorCallback | None = None,
        **connect_options: object,
    ) -> None:
        """Build a stream.

        Args:
            api_key: MAX API access key. Required for private channels.
            api_secret: MAX API secret. Required for private channels.
            uri: WebSocket endpoint.
            reconnect: Convenience switch for reconnects. Ignored when
                `reconnect_policy` is provided.
            reconnect_policy: Backoff/retry settings.
            dispatch: Handler dispatch strategy: `inline`, `task`, or `queue`.
            response_queue: Queue used by `dispatch="queue"`. Created lazily
                when omitted.
            connect_factory: Injectable `websockets.connect`-compatible factory.
            on_connected: Optional lifecycle callback after queued requests are sent.
            on_disconnected: Optional lifecycle callback after a disconnect.
            on_reconnecting: Optional lifecycle callback before sleeping/retrying.
            on_permanent_failure: Optional lifecycle callback before giving up.
            on_handler_error: Optional callback for handler exceptions.
            **connect_options: Extra options forwarded to `websockets.connect`,
                such as `ping_interval`, `ping_timeout`, `close_timeout`, and `max_queue`.
        """
        if dispatch not in {"inline", "task", "queue"}:
            msg = "dispatch must be 'inline', 'task', or 'queue'"
            raise ValueError(msg)

        self.requests = []
        self.handlers = []
        self.uri = uri
        self.reconnect_policy = reconnect_policy or ReconnectPolicy(enabled=reconnect)
        self.dispatch: DispatchMode = dispatch
        self.response_queue = response_queue if response_queue is not None else asyncio.Queue()
        self.connect_factory = connect_factory or cast("ConnectFactory", websockets.connect)
        self.connect_options = connect_options
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.on_reconnecting = on_reconnecting
        self.on_permanent_failure = on_permanent_failure
        self.on_handler_error = on_handler_error
        self._handler_tasks: set[asyncio.Task[object]] = set()

        self.auth(api_key, api_secret)

    def subscribe(self, subscriptions: list[Subscription]) -> None:
        """Queue a `subscribe` request for the given list of subscriptions.

        May be called multiple times; each call sends one `sub` request on each
        connection, including after reconnect.
        """
        self.requests += [Request.subscribe(subscriptions)]

    def auth(self, api_key: str | None, api_secret: str | None) -> None:
        """Queue an `auth` request when credentials are present.

        Called automatically by `__init__`; expose as a method so credentials
        can also be added after construction. Missing credentials are silently
        ignored — public-only streams stay unauthenticated.
        """
        if api_key and api_secret:
            self.requests += [Request.auth(api_key, api_secret)]

    @classmethod
    def from_env(
        cls,
        *,
        uri: str = MAX_WS_URI,
        reconnect: bool = True,
        reconnect_policy: ReconnectPolicy | None = None,
        dispatch: DispatchMode = "inline",
        response_queue: asyncio.Queue[Response] | None = None,
        connect_factory: ConnectFactory | None = None,
        on_connected: LifecycleCallback | None = None,
        on_disconnected: LifecycleCallback | None = None,
        on_reconnecting: LifecycleCallback | None = None,
        on_permanent_failure: LifecycleCallback | None = None,
        on_handler_error: HandlerErrorCallback | None = None,
        **connect_options: object,
    ) -> Stream:
        """Build a stream using `MAX_API_KEY` / `MAX_API_SECRET` from the environment.

        Raises:
            ValueError: Either env var is missing or empty.
        """
        api_key = os.getenv("MAX_API_KEY")
        if not api_key:
            raise ValueError("MAX_API_KEY is not set")

        api_secret = os.getenv("MAX_API_SECRET")
        if not api_secret:
            raise ValueError("MAX_API_SECRET is not set")

        return cls(
            api_key=api_key,
            api_secret=api_secret,
            uri=uri,
            reconnect=reconnect,
            reconnect_policy=reconnect_policy,
            dispatch=dispatch,
            response_queue=response_queue,
            connect_factory=connect_factory,
            on_connected=on_connected,
            on_disconnected=on_disconnected,
            on_reconnecting=on_reconnecting,
            on_permanent_failure=on_permanent_failure,
            on_handler_error=on_handler_error,
            **connect_options,
        )

    def run(self) -> None:
        """Connect and dispatch messages until cancelled.

        Wraps [`arun`][maicoin.ws.Stream.arun] in `asyncio.run`. Use
        [`arun`][maicoin.ws.Stream.arun] directly when you already have an
        event loop.
        """
        asyncio.run(self.arun())

    async def arun(self) -> None:
        """Async entry point: connect, replay queued requests, and dispatch responses forever."""
        retry_count = 0
        while True:
            try:
                async with self.connect_factory(self.uri, **self.connect_options) as ws:
                    retry_count = 0
                    for req in self.requests:
                        await ws.send(req.message())
                    await self._call_lifecycle(self.on_connected, None)

                    while True:
                        data = await ws.recv()
                        resp = Response.model_validate_json(data)
                        await self._dispatch(resp)
            except asyncio.CancelledError:
                await self._cancel_handler_tasks()
                raise
            except Exception as exc:
                await self._call_lifecycle(self.on_disconnected, exc)
                retry_count += 1
                if not self._should_reconnect(retry_count):
                    await self._call_lifecycle(self.on_permanent_failure, exc)
                    raise
                await self._call_lifecycle(self.on_reconnecting, exc)
                delay = self.reconnect_policy.delay(retry_count)
                if delay > 0:
                    await asyncio.sleep(delay)

    def add_handler(self, handler: Handler) -> None:
        """Register a callback invoked with each [`Response`][maicoin.ws.Response].

        In `inline` mode handlers run in registration order. In `task` mode each
        handler is scheduled independently; ordering is not guaranteed. In
        `queue` mode registered handlers are ignored and responses are written to
        [`response_queue`][maicoin.ws.Stream.response_queue].
        """
        self.handlers.append(handler)

    def _should_reconnect(self, retry_count: int) -> bool:
        policy = self.reconnect_policy
        if not policy.enabled:
            return False
        return policy.max_retries is None or retry_count <= policy.max_retries

    async def _dispatch(self, resp: Response) -> None:
        if self.dispatch == "queue":
            await self.response_queue.put(resp)
            return

        for handler in self.handlers:
            if self.dispatch == "task":
                task = asyncio.create_task(self._call_handler(handler, resp))
                self._handler_tasks.add(task)
                task.add_done_callback(self._handler_tasks.discard)
            else:
                await self._call_handler(handler, resp)

    async def _call_handler(self, handler: Handler, resp: Response) -> None:
        try:
            result = handler(resp)
            if inspect.isawaitable(result):
                await result
        except Exception as exc:
            if self.on_handler_error is None:
                if self.dispatch == "inline":
                    raise
                return
            result = self.on_handler_error(exc, resp)
            if inspect.isawaitable(result):
                await result

    async def _call_lifecycle(self, callback: LifecycleCallback | None, exc: Exception | None) -> None:
        if callback is None:
            return
        result = callback(exc)
        if inspect.isawaitable(result):
            await result

    async def _cancel_handler_tasks(self) -> None:
        for task in self._handler_tasks:
            task.cancel()
        if self._handler_tasks:
            await asyncio.gather(*self._handler_tasks, return_exceptions=True)
        self._handler_tasks.clear()
