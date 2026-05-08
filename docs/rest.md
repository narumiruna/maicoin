# 🌐 REST v3 guide

[`maicoin.v3.Client`][maicoin.v3.Client] wraps the [MAX REST v3 API](https://max-api.maicoin.com/doc/v3.html). Public methods need no credentials; private (signed) methods require an API key pair.

## Constructing a client

```python
from maicoin.v3 import Client

public = Client()
private = Client(api_key="...", api_secret="...")
```

You can override the base URL, timeout, or HTTP session if needed:

```python
import httpx
from maicoin.v3 import Client

client = Client(
    api_key="...",
    api_secret="...",
    base_url="https://max-api.maicoin.com",
    timeout=10,
    session=httpx.Client(),
)
```

## Public endpoints

```python
client.timestamp()
client.markets()
client.currencies()
client.ticker("btctwd")
client.tickers(["btctwd", "ethtwd"])
client.depth("btctwd", limit=5)
client.trades("btctwd", limit=10)
client.kline("btctwd", period=1, limit=5)
```

## Private endpoints

```python
client.info()
client.accounts()
client.open_orders(market="btctwd", limit=10)
client.closed_orders(market="btctwd", limit=10)
client.wallet_trades(limit=10)
```

!!! warning "⚠️ Private methods can move money"
    Private methods include order placement, withdrawals, internal transfers, convert orders, and M-Wallet borrow/repay/transfer. Double-check arguments before calling state-changing methods against a live account.

## Raw escape hatch

When you need an endpoint that the typed wrapper doesn't cover, call [`Client.request`][maicoin.v3.Client.request] directly:

```python
client.request("GET", "/api/v3/some/endpoint", auth=True, params={"market": "btctwd"})
```

The raw method returns the parsed JSON payload and applies the same auth/error handling as the typed wrappers.

## Errors

Failed responses raise:

- [`MaxHTTPError`][maicoin.v3.MaxHTTPError] — non-2xx HTTP responses without a recognized API error body.
- [`MaxAPIError`][maicoin.v3.MaxAPIError] — MAX-shaped error payloads (`{"error": {"code": ..., "message": ...}}`).

## Reference

Full method list: [`maicoin.v3` API reference](reference/v3.md).
