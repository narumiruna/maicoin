import asyncio

from maicoin import AuthAction
from maicoin import Channel
from maicoin import Subscription
from maicoin import SubscriptionAction
from maicoin.websocket import subscribe


def main():
    messages = [
        AuthAction.from_env().to_dict(),
        SubscriptionAction([
            Subscription(Channel.BOOK, 'btcusdt', depth=1),
            Subscription(Channel.TRADE, 'btcusdt'),
            Subscription(Channel.TICKER, 'btcusdt'),
            Subscription(Channel.USER, 'btcusdt'),
        ]).to_dict(),
    ]

    asyncio.run(subscribe(messages))


if __name__ == '__main__':
    main()
