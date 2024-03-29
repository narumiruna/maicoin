# maicoin

A Python package for MaiCoin MAX API

## Examples

### WebSocket API

```python
import asyncio

from loguru import logger

from maicoin import AuthAction
from maicoin import Channel
from maicoin import Subscription
from maicoin import SubscriptionAction
from maicoin.websocket import subscribe


def callback(event):
    logger.info(event)


actions = [
    AuthAction.from_env().to_dict(),
    SubscriptionAction([
        Subscription(Channel.BOOK, 'btcusdt', depth=1),
        Subscription(Channel.TRADE, 'btcusdt'),
        Subscription(Channel.TICKER, 'btcusdt'),
    ]).to_dict(),
]

callbacks = [
    callback,
]

asyncio.run(subscribe(actions, callbacks))
```

## To-Do List

- [x] [WebSocket API](https://maicoin.github.io/max-websocket-docs)
  - [x] Public channels
    - [x] Subscribe
    - [x] Unsubscribe
    - [x] Orderbook
    - [x] Trade
    - [x] Ticker
    - [ ] Klin
    - [ ] Market Status
  - [x] Authentication
  - [x] Private channels
    - [x] Order
    - [x] Trade
    - [x] Account
- [ ] [HTTP API](https://max.maicoin.com/documents/api_list/v2)
