import json

import websockets
from loguru import logger

from .parser import parse_response
from .utils import get_max_ws_uri


async def subscribe(messages):
    uri = get_max_ws_uri()
    async with websockets.connect(uri) as websocket:
        for message in messages:
            await websocket.send(json.dumps(message))

        while True:
            try:
                response = await websocket.recv()
                event = parse_response(json.loads(response))
                if event is not None:
                    logger.info(event.event)

            except websockets.ConnectionClosed as e:
                logger.error(e)
                break
