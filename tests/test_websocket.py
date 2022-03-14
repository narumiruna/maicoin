import asyncio

from maicoin import AuthAction
from maicoin import Channel
from maicoin import Subscription
from maicoin import SubscriptionAction
from maicoin import subscribe
from maicoin.utils import get_max_ws_uri


def test_public():
    messages = [
        AuthAction.from_env().to_dict(),
        SubscriptionAction([
            Subscription(Channel.BOOK, 'btcusdt', depth=1),
            Subscription(Channel.TRADE, 'btcusdt'),
            Subscription(Channel.TICKER, 'btcusdt'),
        ]).to_dict(),
    ]

    uri = get_max_ws_uri()
    asyncio.run(subscribe(uri, messages))
