import os

from maicoin.utils import MAX_WS_URI
from maicoin.utils import get_max_ws_uri


def test_get_max_ws_uri():
    assert get_max_ws_uri() == MAX_WS_URI

    uri = 'wss://test-max-stream.maicoin.com/ws'
    os.environ['MAX_WS_URI'] = uri
    assert get_max_ws_uri() == uri
