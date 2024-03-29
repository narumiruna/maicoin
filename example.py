from dotenv import find_dotenv
from dotenv import load_dotenv

from maicoin import Channel
from maicoin import Stream
from maicoin import Subscription


def main():
    load_dotenv(find_dotenv())

    subscriptions = [
        Subscription(Channel.BOOK, market="btcusdt", depth=1),
        Subscription(Channel.BOOK, market="ethusdt", depth=1),
        Subscription(Channel.TICKER, market="btcusdt"),
        Subscription(Channel.TICKER, market="ethusdt"),
        Subscription(Channel.TRADE, market="btcusdt"),
        Subscription(Channel.TRADE, market="ethusdt"),
    ]

    stream = Stream(subscriptions)
    stream.run()


if __name__ == "__main__":
    main()
