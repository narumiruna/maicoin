import json

import websockets
from loguru import logger

from .parser import parse_event
from .utils import get_max_ws_uri


async def subscribe(actions, callbacks):
    uri = get_max_ws_uri()
    async with websockets.connect(uri) as websocket:
        for action in actions:
            await websocket.send(json.dumps(action))
        while True:
            try:
                response = await websocket.recv()
                event = parse_event(json.loads(response))
                for callback in callbacks:
                    callback(event)
            except websockets.ConnectionClosed as e:
                logger.error(e)
                break
