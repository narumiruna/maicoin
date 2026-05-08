from enum import StrEnum


class Channel(StrEnum):
    BOOK = "book"
    TRADE = "trade"
    TICKER = "ticker"
    USER = "user"
    KLINE = "kline"
    MARKET_STATUS = "market_status"
    POOL_QUOTA = "pool_quota"
