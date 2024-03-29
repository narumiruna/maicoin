from __future__ import annotations

import asyncio
import json
import os
from typing import Callable

from loguru import logger
from websockets.client import connect

from .action import Action
from .response import Response
from .subscription import Subscription

MAX_WS_URI = os.environ.get("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")




class Stream:
    subscriptions: list[Subscription]

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

        self.subscriptions = []
        self.handlers = []

    def subscribe(self, subscriptions: list[Subscription]) -> None:
        self.subscriptions += subscriptions

    @classmethod
    def from_env(cls) -> Stream:
        api_key = os.getenv("MAX_API_KEY")
        if not api_key:
            raise ValueError("MAX_API_KEY is not set")

        api_secret = os.getenv("MAX_API_SECRET")
        if not api_secret:
            raise ValueError("MAX_API_SECRET is not set")

        return cls(api_key=api_key, api_secret=api_secret)

    def run(self):
        asyncio.run(self.arun())

    async def arun(self):
        async with connect(MAX_WS_URI) as ws:
            if self.api_key and self.api_secret:
                await ws.send(
                    Action.auth(self.api_key, self.api_secret).model_dump_json(by_alias=True, exclude_none=True)
                )

            if self.subscriptions:
                await ws.send(Action.subscribe(self.subscriptions).model_dump_json(by_alias=True, exclude_none=True))

            while True:
                data = await ws.recv()
                resp = Response.model_validate_json(data)
                self.fire_handlers(resp)

    def add_handler(self, handler: Callable):
        self.handlers.append(handler)

    def fire_handlers(self, response: Response):
        for handler in self.handlers:
            handler(response)
