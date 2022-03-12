import asyncio
import json

import websockets
from loguru import logger

from . import Auth
from . import Channel
from . import Subscription
from . import SubscriptionList
from .utils import get_max_ws_uri


async def subscribe(uri, messages):
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


def main():
    messages = [
        Auth.from_env().to_msg(),
        SubscriptionList([
            Subscription(Channel.BOOK, 'btcusdt', depth=1),
            Subscription(Channel.TRADE, 'btcusdt'),
            Subscription(Channel.TICKER, 'btcusdt'),
            Subscription(Channel.USER, 'btcusdt'),
        ]).to_dict(),
    ]

    uri = get_max_ws_uri()

    asyncio.run(subscribe(uri, messages))


if __name__ == '__main__':
    main()
