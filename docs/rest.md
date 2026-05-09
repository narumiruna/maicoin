# 🌐 REST v3 guide

[`maicoin.v3.Client`][maicoin.v3.Client] wraps the [MAX REST v3 API](https://max-api.maicoin.com/doc/v3.html). Public methods need no credentials; private (signed) methods require an API key pair.

## Constructing a client

```python
from maicoin.v3 import Client

async with Client() as public:
    ticker = await public.ticker("btctwd")

async with Client(api_key="...", api_secret="...") as private:
    accounts = await private.accounts()
```

For small synchronous scripts, every typed method also has an explicit `_sync` convenience wrapper:

```python
client = Client()
ticker = client.ticker_sync("btctwd")
```

`_sync` wrappers use `asyncio.run()`, so code already running in an event loop should call the async methods directly.

You can override the base URL, timeout, retry policy, or HTTP session if needed:

```python
import httpx
from maicoin.v3 import Client, RetryPolicy

client = Client(
    api_key="...",
    api_secret="...",
    base_url="https://max-api.maicoin.com",
    timeout=10,
    retry_policy=RetryPolicy(total_attempts=3),
    session=httpx.AsyncClient(),
)
```

Retries are conservative by default: only idempotent methods (`GET`, `HEAD`, `OPTIONS`) retry transient `429`, `502`, `503`, and `504` responses or network/timeout failures. `Retry-After` is respected when present. State-changing methods such as order placement and withdrawals are not retried unless you explicitly opt in with `RetryPolicy(retry_non_idempotent=True)`.

## Public endpoints

```python
await client.timestamp()
await client.markets()
await client.currencies()
await client.ticker("btctwd")
await client.tickers(["btctwd", "ethtwd"])
await client.depth("btctwd", limit=5)
await client.trades("btctwd", limit=10)
await client.kline("btctwd", period=1, limit=5)
```

## Private endpoints

```python
await client.info()
await client.accounts()
await client.open_orders(market="btctwd", limit=10)
await client.closed_orders(market="btctwd", limit=10)
await client.wallet_trades(limit=10)
```

!!! warning "⚠️ Private methods can move money"
    Private methods include order placement, withdrawals, internal transfers, convert orders, and M-Wallet borrow/repay/transfer. Double-check arguments before calling state-changing methods against a live account.

## Raw escape hatch

When you need an endpoint that the typed wrapper doesn't cover, call [`Client.request`][maicoin.v3.Client.request] directly:

```python
await client.request("GET", "/api/v3/some/endpoint", auth=True, params={"market": "btctwd"})
```

The raw method returns the parsed JSON payload and applies the same auth/error handling as the typed wrappers.

## Errors

Failed responses raise:

- [`MaxHTTPError`][maicoin.v3.MaxHTTPError] — non-2xx HTTP responses without a recognized API error body.
- [`MaxAPIError`][maicoin.v3.MaxAPIError] — MAX-shaped error payloads (`{"error": {"code": ..., "message": ...}}`).

## Reference

Full method list: [`maicoin.v3` API reference](reference/v3.md).
