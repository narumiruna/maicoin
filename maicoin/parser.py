# from .enums import Channel
# from .enums import EventType
# from .events import Event
# from .events import AuthenticatedEvent
# from .events import BookEvent
# from .events import Error
# from .events import OrderEvent
# from .events import SubscribedEvent
# from .events import TickerEvent
# from .events import TradeEvent
# from .events import UnsubscribedEvent

# def parse_public_channel(d: dict):
#     m = {
#         Channel.BOOK: BookEvent.from_dict,
#         Channel.TRADE: TradeEvent.from_dict,
#         Channel.TICKER: TickerEvent.from_dict,
#     }
#     return m[Channel(d.get('c'))](d)

# def parse_event(d: dict):
#     m = {
#         EventType.ERROR: Error.from_dict,
#         EventType.SUBSCRIBED: SubscribedEvent.from_dict,
#         EventType.UNSUBSCRIBED: UnsubscribedEvent.from_dict,
#         EventType.AUTHENTICATED: AuthenticatedEvent.from_dict,
#         EventType.SNAPSHOT: parse_public_channel,
#         EventType.UPDATE: parse_public_channel,
#         EventType.ORDER_SNAPSHOT: OrderEvent.from_dict,
#         EventType.ORDER_UPDATE: OrderEvent.from_dict,
#         EventType.TRADE_SNAPSHOT: TradeEvent.from_dict,
#         EventType.TRADE_UPDATE: TradeEvent.from_dict,
#         EventType.ACCOUNT_SNAPSHOT: Event.from_dict,
#         EventType.ACCOUNT_UPDATE: Event.from_dict,
#     }
#     return m[EventType(d.get('e'))](d)
