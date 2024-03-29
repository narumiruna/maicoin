from __future__ import annotations

import asyncio
import json
import os
from typing import Callable

from loguru import logger
from websockets.client import connect

from .action import Action
from .event import Event
from .subscription import Subscription

MAX_WS_URI = os.environ.get("MAX_WS_URI", "wss://max-stream.maicoin.com/ws")


def _log_event(event: Event) -> None:
    logger.info(event.model_dump(exclude_none=True))


class Stream:
    subscriptions: list[Subscription]

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        log_event: bool = True,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

        self.subscriptions = []
        self.event_handlers = []

        if log_event:
            self.add_event_handler(_log_event)

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
                response = await ws.recv()
                data = json.loads(response)
                event = Event.model_validate(data)
                self.fire_event_handlers(event)

    def add_event_handler(self, event_handler: Callable):
        self.event_handlers.append(event_handler)

    def fire_event_handlers(self, event: Event):
        for event_handler in self.event_handlers:
            event_handler(event)
