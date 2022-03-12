from .websocket import subscribe
from .websocket import get_max_ws_uri

import websockets
import asyncio
import json
from loguru import logger


class Stream(object):

    def __init__(self, parser) -> None:
        self.parser = parser

    def subscribe(self, subscription):
        pass

    async def handler(uri, messages):
        async with websockets.connect(uri) as websocket:
            for message in messages:
                await websocket.send(json.dumps(message))

            while True:
                try:
                    response = await websocket.recv()
                    logger.info(response)
                except websockets.ConnectionClosed as e:
                    logger.error(e)
                    break
