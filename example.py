from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from maicoin.ws import Channel
from maicoin.ws import Response
from maicoin.ws import Stream
from maicoin.ws import Subscription


def log_response(response: Response) -> None:
    logger.info(response.model_dump(exclude_none=True))


load_dotenv(find_dotenv())

subscriptions = [
    Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
    Subscription(channel=Channel.TICKER, market="btcusdt"),
    Subscription(channel=Channel.TRADE, market="btcusdt"),
]

stream = Stream.from_env()
stream.subscribe(subscriptions)
stream.add_handler(log_response)
stream.run()
