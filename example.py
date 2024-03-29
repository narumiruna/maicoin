from dotenv import find_dotenv
from dotenv import load_dotenv

from maicoin.ws import Channel
from maicoin.ws import Stream
from maicoin.ws import Subscription


def main():
    load_dotenv(find_dotenv())

    subscriptions = [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
    ]

    stream = Stream.from_env()
    stream.subscribe(subscriptions)
    stream.run()


if __name__ == "__main__":
    main()
