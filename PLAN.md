# PLAN.md

## Goal

Add the missing MAX REST API v3 support while preserving the existing WebSocket API behavior. The current codebase is centered on `src/maicoin/ws/`; REST support includes the legacy `GET /api/v2/k` K-line endpoint in `src/maicoin/v2/kline.py` and the newer v3 package under `src/maicoin/v3/`.

Official references:

- REST API v3: https://max-api.maicoin.com/doc/v3.html
- WebSocket API: https://maicoin.github.io/max-websocket-docs/

## Current State

### Implemented

- WebSocket public channels: book, trade, ticker, kline, and market_status.
- Basic WebSocket private response models for order, trade, and account events.
- WebSocket auth, subscribe, unsubscribe request models, and stream helper.
- REST v2: only `GET /api/v2/k` K-line lookup.
- REST v3 foundation package under `maicoin/v3/`.
- REST API v3 authentication helpers for `X-MAX-ACCESSKEY`, `X-MAX-PAYLOAD`, and `X-MAX-SIGNATURE`.
- REST API v3 low-level sync `Client.request(...)` using `httpx` with public/private request support.
- REST API v3 HTTP/API error classes.
- REST API v3 public endpoint wrappers and Pydantic models for markets, currencies, timestamp, k, depth, trades, tickers, ticker, and m-wallet public rates/limits.
- REST API v3 private endpoint wrappers and models for accounts, open/closed/history orders, create/cancel order, and order trades.
- Tests for WebSocket request, response, and subscription model validation.
- Tests for v3 auth signatures, query/body placement, authenticated headers, error handling, public/private endpoint request construction, and response parsing.

### Missing

- REST API v3 private endpoints: withdrawals, deposits, fund transactions, convert, and m-wallet loan/repayment/liquidation/interest/transfer endpoints.
- REST API tests for withdrawals, deposits, fund transactions, convert, and m-wallet private endpoint wrappers and response parsing.
- WebSocket models for newer documented features: MWallet Pool Quota, Fast Trade, MWallet private channels, and book sequence/version fields `fi`, `li`, and `v`.

## Design Direction

### Package Layout

Add `src/maicoin/v3/` without replacing `src/maicoin/v2/`, so existing imports remain compatible.

Suggested structure:

```text
src/maicoin/v3/
  __init__.py
  auth.py          # payload/signature/header generation
  client.py        # sync HTTP client and shared request logic
  errors.py        # API/HTTP errors
  models.py        # shared enums/base models, or split by domain later
  public.py        # public endpoints
  order.py         # order endpoints and models
  trade.py         # trade endpoints and models
  wallet.py        # accounts, deposit, withdrawal, m-wallet
  transaction.py   # fund transactions/transfers/rewards
  convert.py       # convert endpoints
```

Use a synchronous client backed by `httpx`. Add an async client later only if needed.

### Client API

Provide two layers:

1. Low-level `Client.request(method, path, params=None, auth=False)` to centralize base URL, timeout, JSON handling, errors, and authentication.
2. High-level domain methods, for example:
   - `client.markets()`
   - `client.kline(market="btctwd", period=1, limit=30)`
   - `client.order(market="btctwd", order_id=...)`
   - `client.create_order(...)`

### Authentication

According to the v3 documentation, private endpoint payloads must include:

- `nonce`
- request parameters
- `path`

JSON-serialize that object, Base64-encode it, sign the payload with HMAC-SHA256 using the secret key, and send these headers:

- `X-MAX-ACCESSKEY`
- `X-MAX-PAYLOAD`
- `X-MAX-SIGNATURE`
- `Content-Type: application/json`

GET parameters go in the query string. DELETE/POST/PUT parameters go in the JSON body. Tests should use a fixed nonce so signatures are reproducible.

## Implementation Phases

### Phase 1: v3 Foundation

Complete. `maicoin/v3/` now contains auth helpers, a sync low-level client, error classes, and unit tests. Public endpoints are callable through `Client.request(...)` without API credentials.

### Phase 2: v3 Public Endpoints

Complete. Public endpoint wrappers now cover markets, currencies, timestamp, k, depth, trades, tickers, ticker, and m-wallet public index/limit/rate endpoints with Pydantic parsing tests.

### Phase 3: v3 Private Auth, Accounts, and Orders

Complete. Authenticated client wrappers now cover accounts, open/closed/history orders, order lookup, create/cancel order, cancel all orders, and order trades with Pydantic parsing tests.

### Phase 4: Transaction and Funds Features

Add withdrawals, deposits, fund transactions, convert, rewards, and internal transfers. Tests must not send real state-changing requests.

### Phase 5: M-Wallet

Add m-wallet public/private endpoints: index prices, limits, interest rates, loan, repayment, transfers, liquidations, interests, and AD ratio.

### Phase 6: WebSocket Gap Cleanup

Add WebSocket support for MWallet Pool Quota, Fast Trade, MWallet private channels, and book sequence/version fields.

## Acceptance Criteria

Before completing each phase, run at least:

```shell
uv run ruff check .
uv run ty check .
uv run pytest -v -s --cov=src --cov-report=xml tests
```

REST private endpoint tests should use mocked transport/session objects. Do not use real API keys or send real order/withdrawal requests.
