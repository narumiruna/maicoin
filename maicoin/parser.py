from loguru import logger

from .auth import AuthenticatedEvent
from .book import BookEvent
from .channel import Channel
from .event import Event
from .subscription import SubscribedEvent
from .subscription import UnsubscribedEvent
from .ticker import TickerEvent
from .trade import TradeEvent


def parse_public_channel(d: dict):
    print(d.get('c'))
    m = {
        Channel.BOOK: BookEvent.from_dict,
        Channel.TRADE: TradeEvent.from_dict,
        Channel.TICKER: TickerEvent.from_dict,
    }
    return m[Channel(d.get('c'))](d)


def parse_response(d: dict):
    m = {
        Event.ERROR: logger.info,
        Event.SUBSCRIBED: SubscribedEvent.from_dict,
        Event.UNSUBSCRIBED: UnsubscribedEvent.from_dict,
        Event.AUTHENTICATED: AuthenticatedEvent.from_dict,
        Event.SNAPSHOT: parse_public_channel,
        Event.UPDATE: parse_public_channel,
        Event.ORDER_SNAPSHOT: logger.info,
        Event.ORDER_UPDATE: logger.info,
        Event.TRADE_SNAPSHOT: logger.info,
        Event.TRADE_UPDATE: logger.info,
        Event.ACCOUNT_SNAPSHOT: logger.info,
        Event.ACCOUNT_UPDATE: logger.info,
    }
    return m[Event(d.get('e'))](d)
