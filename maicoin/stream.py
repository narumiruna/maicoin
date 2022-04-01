import asyncio
import json
from typing import Callable
from typing import List

from loguru import logger
from websockets.client import WebSocketClientProtocol
from websockets.legacy.client import Connect

from .data import Event
from .data import Subscription
from .data import create_authorize_action
from .data import create_subscribe_action
from .utils import get_api_key_from_env
from .utils import get_api_secret_from_env
from .utils import get_max_ws_uri


class Stream(object):
    protocol: WebSocketClientProtocol

    def __init__(self,
                 subscriptions: List[Subscription] = None,
                 api_key: str = None,
                 api_secret: str = None,
                 log_event: bool = True) -> None:
        self.subscriptions = subscriptions or []
        self.api_key = api_key or get_api_key_from_env()
        self.api_secret = api_secret or get_api_secret_from_env()

        self.protocol = None
        self.event_handlers = []

        if log_event:
            self.add_event_handler(lambda event: logger.info(event))

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_loop())
        finally:
            loop.close()

    async def run_loop(self):
        uri = get_max_ws_uri()
        async with Connect(uri) as self.protocol:
            await self.authorize()
            await self.subscribe()
            while True:
                response = await self.recv()
                event = Event.from_dict(response)
                self.fire_event_handlers(event)

    async def send(self, obj: dict):
        message = json.dumps(obj)
        await self.protocol.send(message)

    async def recv(self) -> dict:
        response = await self.protocol.recv()
        return json.loads(response)

    async def subscribe(self):
        await self.send(create_authorize_action(self.api_key, self.api_secret).to_dict())

    async def authorize(self):
        await self.send(create_subscribe_action(self.subscriptions).to_dict())

    def add_event_handler(self, event_handler: Callable):
        self.event_handlers.append(event_handler)

    def fire_event_handlers(self, event: Event):
        for event_handler in self.event_handlers:
            event_handler(event)
