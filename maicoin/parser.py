from .account import AccountEvent
from .auth import AuthenticatedEvent
from .book import BookEvent
from .channel import Channel
from .error import Error
from .event import Event
from .order import OrderEvent
from .subscription import SubscribedEvent
from .subscription import UnsubscribedEvent
from .ticker import TickerEvent
from .trade import TradeEvent


def parse_public_channel(d: dict):
    m = {
        Channel.BOOK: BookEvent.from_dict,
        Channel.TRADE: TradeEvent.from_dict,
        Channel.TICKER: TickerEvent.from_dict,
    }
    return m[Channel(d.get('c'))](d)


def parse_response(d: dict):
    m = {
        Event.ERROR: Error.from_dict,
        Event.SUBSCRIBED: SubscribedEvent.from_dict,
        Event.UNSUBSCRIBED: UnsubscribedEvent.from_dict,
        Event.AUTHENTICATED: AuthenticatedEvent.from_dict,
        Event.SNAPSHOT: parse_public_channel,
        Event.UPDATE: parse_public_channel,
        Event.ORDER_SNAPSHOT: OrderEvent.from_dict,
        Event.ORDER_UPDATE: OrderEvent.from_dict,
        Event.TRADE_SNAPSHOT: TradeEvent.from_dict,
        Event.TRADE_UPDATE: TradeEvent.from_dict,
        Event.ACCOUNT_SNAPSHOT: AccountEvent.from_dict,
        Event.ACCOUNT_UPDATE: AccountEvent.from_dict,
    }
    return m[Event(d.get('e'))](d)
