# 🚀 Quick start

## REST

```python
from maicoin.v3 import Client

client = Client()                                  # public-only
client = Client(api_key=..., api_secret=...)       # private (signed)

client.ticker("btctwd")
client.markets()
client.depth("btctwd", limit=5)
client.kline("btctwd", period=1, limit=5)
```

For private calls:

```python
client.info()
client.accounts()
client.open_orders(market="btctwd")
```

## WebSocket

```python
from maicoin.ws import Channel, Stream, Subscription

stream = Stream()  # public channels only
stream.subscribe(
    [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
    ]
)
stream.add_handler(lambda r: print(r.model_dump(exclude_none=True)))
stream.run()
```

For private channels (orders, balances, M-Wallet events) construct the stream from your environment:

```python
stream = Stream.from_env()  # reads MAX_API_KEY / MAX_API_SECRET
```

## Runnable examples

- [`examples/rest.py`](https://github.com/narumiruna/maicoin/blob/main/examples/rest.py)
- [`examples/websocket.py`](https://github.com/narumiruna/maicoin/blob/main/examples/websocket.py)
