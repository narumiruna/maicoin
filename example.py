from dotenv import find_dotenv
from dotenv import load_dotenv
from rich import print

from maicoin.ws import Channel
from maicoin.ws import Response
from maicoin.ws import Stream
from maicoin.ws import Subscription


def print_response_details(response: Response) -> None:
    print(response.model_dump(exclude_none=True))


def main() -> None:
    load_dotenv(find_dotenv())

    subscriptions = [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
        Subscription(channel=Channel.KLINE, market="btcusdt"),
        Subscription(channel=Channel.MARKET_STATUS),
    ]

    stream = Stream.from_env()
    stream.subscribe(subscriptions)
    stream.add_handler(print_response_details)
    stream.run()


if __name__ == "__main__":
    main()
