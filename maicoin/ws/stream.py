from __future__ import annotations

import asyncio
import os
from typing import Callable

import websockets

from .request import Request
from .response import Response
from .subscription import Subscription

MAX_WS_URI = os.environ.get("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")


class Stream:
    requests: list[Request]
    handlers: list[Callable]

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.requests = []
        self.handlers = []

        self.auth(api_key, api_secret)

    def subscribe(self, subscriptions: list[Subscription]) -> None:
        self.requests += [Request.subscribe(subscriptions)]

    def auth(self, api_key: str, api_secret: str) -> None:
        if api_key and api_secret:
            self.requests += [Request.auth(api_key, api_secret)]

    @classmethod
    def from_env(cls) -> Stream:
        api_key = os.getenv("MAX_API_KEY")
        if not api_key:
            raise ValueError("MAX_API_KEY is not set")

        api_secret = os.getenv("MAX_API_SECRET")
        if not api_secret:
            raise ValueError("MAX_API_SECRET is not set")

        return cls(api_key=api_key, api_secret=api_secret)

    def run(self) -> None:
        asyncio.run(self.arun())

    async def arun(self) -> None:
        async with websockets.connect(MAX_WS_URI) as ws:
            for req in self.requests:
                await ws.send(req.message())

            while True:
                data = await ws.recv()
                resp = Response.model_validate_json(data)
                for handler in self.handlers:
                    handler(resp)

    def add_handler(self, handler: Callable) -> None:
        self.handlers.append(handler)
