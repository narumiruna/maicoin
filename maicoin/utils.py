import os
from datetime import datetime

MAX_WS_URI = "wss://max-stream.maicoin.com/ws"


def get_max_ws_uri():
    max_ws_uri = os.environ.get("MAX_WS_URI")

    if max_ws_uri is None:
        max_ws_uri = MAX_WS_URI

    return max_ws_uri


def get_api_key_from_env():
    return os.environ.get("MAX_API_KEY")


def get_api_secret_from_env():
    return os.environ.get("MAX_API_SECRET")


def to_datetime(timestamp: int):
    return datetime.fromtimestamp(int(timestamp) / 1000)
