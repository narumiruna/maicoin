import asyncio
import json
from typing import List

import websockets
from loguru import logger
from websockets.client import WebSocketClientProtocol

from .auth import AuthAction
from .parser import parse_event
from .subscription import Subscription
from .subscription import SubscriptionAction
from .utils import get_max_ws_uri


class Stream(object):
    websocket: WebSocketClientProtocol

    def __init__(self, subscriptions: List[Subscription]) -> None:
        self.subscriptions = subscriptions
        self.websocket = None

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_loop())
        finally:
            loop.close()

    async def run_loop(self):
        uri = get_max_ws_uri()
        async with websockets.connect(uri) as self.websocket:
            await self.authorize()
            await self.subscribe()

            while True:
                response = await self.recv()
                logger.info(response)

    async def send(self, obj: dict):
        message = json.dumps(obj)
        await self.websocket.send(message)

    async def recv(self) -> dict:
        response = await self.websocket.recv()
        return parse_event(json.loads(response))

    async def subscribe(self):
        action = SubscriptionAction(self.subscriptions).to_dict()
        await self.send(action)

    async def authorize(self):
        action = AuthAction.from_env().to_dict()
        await self.send(action)
