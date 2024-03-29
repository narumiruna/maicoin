from dotenv import find_dotenv
from dotenv import load_dotenv

from maicoin import Channel
from maicoin import Stream
from maicoin import Subscription


def main():
    load_dotenv(find_dotenv())

    subscriptions = [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.BOOK, market="ethusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TICKER, market="ethusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="ethusdt"),
    ]

    stream = Stream.from_env()
    stream.subscribe(subscriptions)
    stream.run()


if __name__ == "__main__":
    main()
