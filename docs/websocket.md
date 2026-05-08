# 📡 WebSocket guide

[`maicoin.ws.Stream`][maicoin.ws.Stream] connects to the [MAX WebSocket API](https://maicoin.github.io/max-websocket-docs/), sends subscription/auth requests, and dispatches each incoming message to registered handlers as a typed [`Response`][maicoin.ws.Response].

## Public channels

```python
from maicoin.ws import Channel, Stream, Subscription

stream = Stream()
stream.subscribe(
    [
        Subscription(channel=Channel.BOOK, market="btcusdt", depth=5),
        Subscription(channel=Channel.TICKER, market="btcusdt"),
        Subscription(channel=Channel.TRADE, market="btcusdt"),
        Subscription(channel=Channel.KLINE, market="btcusdt"),
        Subscription(channel=Channel.MARKET_STATUS),
    ]
)
stream.add_handler(lambda r: print(r.model_dump(exclude_none=True)))
stream.run()
```

## Private channels

Private channels (user orders, balances, M-Wallet events) require credentials. Use [`Stream.from_env`][maicoin.ws.Stream.from_env] to construct the stream from `MAX_API_KEY` / `MAX_API_SECRET`:

```python
stream = Stream.from_env()
stream.subscribe(
    [
        Subscription(channel=Channel.ORDER),
        Subscription(channel=Channel.TRADE_UPDATE),
        Subscription(channel=Channel.BALANCE_UPDATE),
    ]
)
```

Or pass them explicitly:

```python
stream = Stream(api_key="...", api_secret="...")
```

## Handlers

Handlers receive a fully validated [`Response`][maicoin.ws.Response]. You can attach as many handlers as you like:

```python
def on_response(response):
    if response.event == "ticker":
        ...

stream.add_handler(on_response)
```

## Async usage

`Stream.run()` wraps `asyncio.run`. To integrate with an existing event loop, use [`arun`][maicoin.ws.Stream.arun]:

```python
import asyncio

async def main():
    stream = Stream.from_env()
    stream.subscribe([...])
    stream.add_handler(...)
    await stream.arun()

asyncio.run(main())
```

## Configuring the URI

`Stream` reads the WebSocket URI from `MAX_WS_URI`, defaulting to `wss://max-stream.maicoin.com/ws`. Override it for staging or testing:

```dotenv
MAX_WS_URI=wss://your-staging-host/ws
```

## Reference

Full module: [`maicoin.ws` API reference](reference/ws.md).
