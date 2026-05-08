# maicoin 🪙

Python client for the [MaiCoin MAX](https://max.maicoin.com/) exchange. Provides a typed REST v3 client and a WebSocket stream client built on `httpx`, `websockets`, and `pydantic`.

## ✨ Highlights

- 🌐 **REST v3** — typed wrappers over public and private MAX endpoints, with a raw `request()` escape hatch.
- 📡 **WebSocket** — subscription-based stream client with Pydantic-validated responses.
- 🔐 **Auth helpers** — nonce, payload encoding, and signature utilities for MAX private endpoints.
- 🐍 **Modern Python** — Python 3.12+, full type hints, ships `py.typed`.

## 🚀 Quick start

```shell
uv add maicoin
# or
pip install maicoin
```

```python
from maicoin.v3 import Client

client = Client()
print(client.ticker("btctwd"))
```

```python
from maicoin.ws import Channel, Stream, Subscription

stream = Stream()
stream.subscribe([Subscription(channel=Channel.TICKER, market="btcusdt")])
stream.add_handler(lambda r: print(r.model_dump(exclude_none=True)))
stream.run()
```

See the [REST guide](rest.md), the [WebSocket guide](websocket.md), and the [API reference](reference/v3.md).

## 📚 References

- HTTP API v3: <https://max-api.maicoin.com/doc/v3.html>
- WebSocket API: <https://maicoin.github.io/max-websocket-docs/>
- Source: <https://github.com/narumiruna/maicoin>

## 📄 License

[MIT](https://github.com/narumiruna/maicoin/blob/main/LICENSE)
