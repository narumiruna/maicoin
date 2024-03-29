from enum import Enum


class ActionType(str, Enum):
    Subscribe = "sub"
    Authorize = "auth"
