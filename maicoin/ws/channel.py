from enum import Enum


class Channel(str, Enum):
    BOOK = "book"
    TRADE = "trade"
    TICKER = "ticker"
    USER = "user"
    KLINE = "kline"
    MARKET_STATUS = "market_status"
