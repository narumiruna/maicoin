from enum import Enum


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    POST_ONLY = "post_only"
    IOC_LIMIT = "ioc_limit"


class OrderState(str, Enum):
    CANCEL = "cancel"
    WAIT = "wait"
    DONE = "done"
    CONVERT = "convert"
    FINALIZING = "finalizing"
    FAILED = "failed"
