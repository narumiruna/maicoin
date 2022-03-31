from maicoin import Channel
from maicoin import Stream
from maicoin import Subscription


def main():
    subscriptions = [
        Subscription(Channel.BOOK, market='btcusdt', depth=1),
        Subscription(Channel.TICKER, market='ethusdt'),
        Subscription(Channel.TRADE, market='btcusdt')
    ]

    stream = Stream(subscriptions)
    stream.run()


if __name__ == '__main__':
    main()
