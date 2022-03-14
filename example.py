import asyncio

from loguru import logger

from maicoin import AuthAction
from maicoin import Channel
from maicoin import Subscription
from maicoin import SubscriptionAction
from maicoin.websocket import subscribe


def callback(event):
    logger.info(event)


def main():
    actions = [
        AuthAction.from_env().to_dict(),
        SubscriptionAction([
            Subscription(Channel.BOOK, 'btcusdt', depth=1),
            Subscription(Channel.TRADE, 'btcusdt'),
            Subscription(Channel.TICKER, 'btcusdt'),
        ]).to_dict(),
    ]

    callbacks = [
        callback,
    ]

    asyncio.run(subscribe(actions, callbacks))


if __name__ == '__main__':
    main()
