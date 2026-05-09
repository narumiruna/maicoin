"""WebSocket stream client for the [MaiCoin MAX WebSocket API](https://maicoin.github.io/max-websocket-docs/).

The client opens a single connection, queues subscription/auth requests, and
dispatches each incoming message to every registered handler as a typed
[`Response`][maicoin.ws.Response].
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable

import websockets

from maicoin.ws.request import Request
from maicoin.ws.response import Response
from maicoin.ws.subscription import Subscription

MAX_WS_URI = os.getenv("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")
"""WebSocket endpoint. Override with the `MAX_WS_URI` env var (e.g. for staging)."""


class Stream:
    """Synchronous-style wrapper around the MAX WebSocket connection.

    Build the stream, call [`subscribe`][maicoin.ws.Stream.subscribe] /
    [`add_handler`][maicoin.ws.Stream.add_handler] as many times as you like,
    then call [`run`][maicoin.ws.Stream.run] to block on the event loop.

    Examples:
        Public channels only:

        >>> from maicoin.ws import Channel, Stream, Subscription
        >>> stream = Stream()
        >>> stream.subscribe([Subscription(channel=Channel.TICKER, market="btcusdt")])
        >>> stream.add_handler(lambda r: print(r.event))
        >>> stream.run()  # doctest: +SKIP

        Private channels (auth):

        >>> stream = Stream.from_env()  # doctest: +SKIP
    """

    requests: list[Request]
    """Pending requests sent in order on connect (auth first if configured)."""

    handlers: list[Callable]
    """Callbacks invoked with each parsed [`Response`][maicoin.ws.Response]."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        """Build a stream.

        When both credentials are provided, an auth request is queued ahead of
        any subscription requests so private channels can be used.

        Args:
            api_key: MAX API access key. Required for private channels.
            api_secret: MAX API secret. Required for private channels.
        """
        self.requests = []
        self.handlers = []

        self.auth(api_key, api_secret)

    def subscribe(self, subscriptions: list[Subscription]) -> None:
        """Queue a `subscribe` request for the given list of subscriptions.

        May be called multiple times; each call sends one `sub` request on
        connect.
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
    def from_env(cls) -> Stream:
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

        return cls(api_key=api_key, api_secret=api_secret)

    def run(self) -> None:
        """Connect and dispatch messages until cancelled.

        Wraps [`arun`][maicoin.ws.Stream.arun] in `asyncio.run`. Use
        [`arun`][maicoin.ws.Stream.arun] directly when you already have an
        event loop.
        """
        asyncio.run(self.arun())

    async def arun(self) -> None:
        """Async entry point: connect, send queued requests, and dispatch responses forever."""
        async with websockets.connect(MAX_WS_URI) as ws:
            for req in self.requests:
                await ws.send(req.message())

            while True:
                data = await ws.recv()
                resp = Response.model_validate_json(data)
                for handler in self.handlers:
                    handler(resp)

    def add_handler(self, handler: Callable) -> None:
        """Register a callback invoked with each [`Response`][maicoin.ws.Response].

        Handlers run in registration order. They should be cheap and
        non-blocking — heavy work belongs in a background task or queue.
        """
        self.handlers.append(handler)
