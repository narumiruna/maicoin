import asyncio

from maicoin import Auth
from maicoin import Channel
from maicoin import Subscription
from maicoin import SubscriptionList
from maicoin.utils import get_max_ws_uri
from maicoin.websocket import subscribe


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
