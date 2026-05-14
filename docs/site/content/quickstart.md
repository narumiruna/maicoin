# 🚀 Quick start

## REST

```python
from maicoin.v3 import Client

async with Client() as client:  # public-only
    await client.ticker("btctwd")
    await client.markets()
    await client.depth("btctwd", limit=5)
    await client.kline("btctwd", period=1, limit=5)
```

For private calls:

```python
async with Client(api_key=..., api_secret=...) as client:
    await client.info()
    await client.accounts()
    await client.open_orders(market="btctwd")
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
