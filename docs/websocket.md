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

## Handlers and dispatch modes

Handlers receive a fully validated [`Response`][maicoin.ws.Response]. You can attach as many handlers as you like:

```python
def on_response(response):
    if response.event == "ticker":
        ...

stream.add_handler(on_response)
```

`Stream` supports three dispatch modes:

- `inline` (default): call/await handlers before reading the next message. This preserves strict ordering.
- `task`: schedule each handler with `asyncio.create_task()`. This keeps slow async handlers from blocking the receive loop, but ordering is not guaranteed.
- `queue`: put responses into `stream.response_queue` for consumer-managed processing; registered handlers are ignored.

```python
stream = Stream(dispatch="task", on_handler_error=lambda exc, response: print(exc))

queue_stream = Stream(dispatch="queue")
# elsewhere: response = await queue_stream.response_queue.get()
```

## Reconnects and heartbeat options

By default, `Stream` reconnects after transient disconnects and replays queued auth/subscription requests. Configure backoff with [`ReconnectPolicy`][maicoin.ws.ReconnectPolicy], or disable reconnects with `reconnect=False`:

```python
from maicoin.ws import ReconnectPolicy

stream = Stream(
    reconnect_policy=ReconnectPolicy(max_retries=10, base_delay=1, max_delay=30),
    ping_interval=20,
    ping_timeout=20,
    close_timeout=5,
)
```

Extra keyword arguments are forwarded to `websockets.connect`, including heartbeat and queue options such as `ping_interval`, `ping_timeout`, `close_timeout`, and `max_queue`.

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
