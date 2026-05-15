import os

from dotenv import find_dotenv
from dotenv import load_dotenv
from rich import print

from maicoin.ws import Channel
from maicoin.ws import Filter
from maicoin.ws import Response
from maicoin.ws import Stream
from maicoin.ws import Subscription


def print_response_details(response: Response) -> None:
    print(response.model_dump(exclude_none=True))


def main() -> None:
    load_dotenv(find_dotenv())
    api_key = os.environ.get("MAX_API_KEY")
    api_secret = os.environ.get("MAX_API_SECRET")

    subscriptions = [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
        Subscription(channel=Channel.KLINE, market="btcusdt"),
        Subscription(channel=Channel.MARKET_STATUS),
    ]

    if api_key and api_secret:
        stream = Stream(
            api_key=api_key,
            api_secret=api_secret,
            auth_filters=[Filter.ORDER, Filter.TRADE, Filter.ACCOUNT],
        )
    else:
        stream = Stream()
        print("[yellow]MAX_API_KEY / MAX_API_SECRET not set — using public WebSocket channels only[/yellow]")

    stream.subscribe(subscriptions)
    stream.add_handler(print_response_details)
    stream.run()


if __name__ == "__main__":
    main()
