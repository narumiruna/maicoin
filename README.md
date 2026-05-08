# maicoin 🪙

Python client for the [MaiCoin MAX](https://max.maicoin.com/) exchange. Provides typed dataclass REST v3 models and a WebSocket stream client built on `httpx`, `websockets`, and `orjson`.

## 📦 Installation

```shell
uv add maicoin
# or
pip install maicoin
```

Requires Python 3.12+.

## 🚀 Quick start

Set credentials in your environment (or a `.env` file):

```dotenv
MAX_API_KEY=your_key
MAX_API_SECRET=your_secret
```

### 🌐 REST

```python
from maicoin.v3 import Client

client = Client()                  # public endpoints
client = Client(api_key=..., api_secret=...)  # private endpoints (signed)

client.ticker("btctwd")
client.accounts()
client.request("GET", "/api/v3/...", auth=True)  # raw escape hatch
```

> [!WARNING]
> ⚠️ Private methods can place orders, transfer funds, take loans, and trigger withdrawals. Double-check arguments before calling state-changing methods against a live account.

### 📡 WebSocket

```python
from maicoin.ws import Channel, Stream, Subscription

stream = Stream()                  # or Stream.from_env() for private channels
stream.subscribe([Subscription(channel=Channel.TICKER, market="btcusdt")])
stream.add_handler(lambda r: print(r.model_dump(exclude_none=True)))
stream.run()
```

Full runnable scripts: [`examples/rest.py`](examples/rest.py), [`examples/websocket.py`](examples/websocket.py).

## 🛠️ Development

This repo uses [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just):

```shell
uv sync
just         # format, lint, type-check, test
just test    # pytest with coverage
```

### Live integration tests

Live tests call the real MAX API and are skipped unless explicitly enabled:

```shell
RUN_LIVE_TESTS=1 uv run pytest -v -s -m live tests/live
# or
just live-test
```

Private read-only live tests also require `MAX_API_KEY` and `MAX_API_SECRET`; `just` loads these from `.env` automatically. Set `MAX_LIVE_MARKET` to override the default public test market (`btctwd`). Destructive live tests are intentionally not implemented yet.

## 📚 References

- HTTP API v3: <https://max-api.maicoin.com/doc/v3.html>
- WebSocket API: <https://maicoin.github.io/max-websocket-docs/>

## 📄 License

[MIT](LICENSE)
