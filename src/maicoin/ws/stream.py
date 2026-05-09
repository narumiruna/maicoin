"""WebSocket stream client for the [MaiCoin MAX WebSocket API](https://maicoin.github.io/max-websocket-docs/).

The client opens a connection, queues subscription/auth requests, and dispatches
incoming messages to registered handlers as typed [`Response`][maicoin.ws.Response]
objects. It can also reconnect with backoff and replay queued requests after a
transient disconnect.
"""

from __future__ import annotations

import asyncio
import os
from typing import cast

import websockets

from maicoin.ws._stream.dispatch import ResponseDispatcher
from maicoin.ws._stream.lifecycle import call_lifecycle
from maicoin.ws._stream.reconnect import ReconnectLoop
from maicoin.ws._stream.reconnect import ReconnectPolicy
from maicoin.ws._stream.reconnect import should_reconnect
from maicoin.ws._stream.session import ConnectedSession
from maicoin.ws._stream.types import ConnectFactory
from maicoin.ws._stream.types import DispatchMode
from maicoin.ws._stream.types import Handler
from maicoin.ws._stream.types import HandlerErrorCallback
from maicoin.ws._stream.types import LifecycleCallback
from maicoin.ws._stream.types import WebSocketConnection
from maicoin.ws._stream.types import WebSocketContext
from maicoin.ws.request import Request
from maicoin.ws.response import Response
from maicoin.ws.subscription import Subscription

__all__ = [
    "MAX_WS_URI",
    "ConnectFactory",
    "DispatchMode",
    "Handler",
    "HandlerErrorCallback",
    "LifecycleCallback",
    "ReconnectPolicy",
    "Stream",
    "WebSocketConnection",
    "WebSocketContext",
]

MAX_WS_URI = os.getenv("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")
"""WebSocket endpoint. Override with the `MAX_WS_URI` env var (e.g. for staging)."""


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
        self._dispatcher = ResponseDispatcher(
            dispatch=dispatch,
            handlers=self.handlers,
            response_queue=self.response_queue,
            on_handler_error=on_handler_error,
        )
        self._handler_tasks = self._dispatcher._handler_tasks

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
        session = ConnectedSession(
            requests=self.requests,
            dispatcher=self._dispatcher,
            on_connected=self.on_connected,
        )
        loop = ReconnectLoop(
            uri=self.uri,
            connect_factory=self.connect_factory,
            connect_options=self.connect_options,
            reconnect_policy=self.reconnect_policy,
            run_connected=session.run,
            on_disconnected=self.on_disconnected,
            on_reconnecting=self.on_reconnecting,
            on_permanent_failure=self.on_permanent_failure,
        )
        try:
            await loop.run()
        except asyncio.CancelledError:
            await self._cancel_handler_tasks()
            raise

    def add_handler(self, handler: Handler) -> None:
        """Register a callback invoked with each [`Response`][maicoin.ws.Response].

        In `inline` mode handlers run in registration order. In `task` mode each
        handler is scheduled independently; ordering is not guaranteed. In
        `queue` mode registered handlers are ignored and responses are written to
        [`response_queue`][maicoin.ws.Stream.response_queue].
        """
        self.handlers.append(handler)

    def _should_reconnect(self, retry_count: int) -> bool:
        return should_reconnect(self.reconnect_policy, retry_count)

    async def _dispatch(self, resp: Response) -> None:
        await self._dispatcher.dispatch_response(resp)

    async def _call_handler(self, handler: Handler, resp: Response) -> None:
        await self._dispatcher.call_handler(handler, resp)

    async def _call_lifecycle(self, callback: LifecycleCallback | None, exc: Exception | None) -> None:
        await call_lifecycle(callback, exc)

    async def _cancel_handler_tasks(self) -> None:
        await self._dispatcher.cancel_handler_tasks()
