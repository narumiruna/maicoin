from enum import Enum


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"
    BID = "bid"
    ASK = "ask"
