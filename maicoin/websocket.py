import json

import websockets
from loguru import logger

from .events import parse_response


async def subscribe(uri, messages):
    async with websockets.connect(uri) as websocket:
        for message in messages:
            await websocket.send(json.dumps(message))

        while True:
            try:
                response = await websocket.recv()
                event = parse_response(json.loads(response))
                if event is not None:
                    logger.info(event)

            except websockets.ConnectionClosed as e:
                logger.error(e)
                break
