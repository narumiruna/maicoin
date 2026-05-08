# PLAN.md

## Goal

Add the missing MAX REST API v3 support while preserving the existing WebSocket API behavior. The current codebase is centered on `maicoin/ws/`; REST support only contains the single `GET /api/v2/k` K-line endpoint in `maicoin/v2/kline.py`. The README also still marks the HTTP API as unfinished, so the next implementation target should be a new `maicoin/v3/` package.

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
- REST API v3 low-level sync `Client.request(...)` using `requests` with public/private request support.
- REST API v3 HTTP/API error classes.
- Tests for WebSocket request, response, and subscription model validation.
- Tests for v3 auth signatures, query/body placement, authenticated headers, and error handling.

### Missing

- REST API v3 high-level public/private endpoint wrappers.
- REST API v3 public endpoints: markets, currencies, timestamp, k, depth, trades, tickers, ticker, index prices, and m-wallet public rates/limits.
- REST API v3 private endpoints: orders, trades, accounts, withdrawals, deposits, fund transactions, convert, and m-wallet loan/repayment/liquidation/interest/transfer endpoints.
- v3 request/response Pydantic models and error handling.
- REST API tests for auth signatures, query/body placement, and response parsing.
- WebSocket models for newer documented features: MWallet Pool Quota, Fast Trade, MWallet private channels, and book sequence/version fields `fi`, `li`, and `v`.

## Design Direction

### Package Layout

Add `maicoin/v3/` without replacing `maicoin/v2/`, so existing imports remain compatible.

Suggested structure:

```text
maicoin/v3/
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

Start with a synchronous client using the existing `requests` dependency. Add an async client later only if needed.

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

Implement public endpoints first because they can be tested without real credentials. Prioritize markets, currencies, timestamp, k, depth, trades, tickers, and ticker.

### Phase 3: v3 Private Auth, Accounts, and Orders

Implement auth headers, private request path signing, accounts, open/closed/history orders, create/cancel order, and order trades. This is the minimum useful trading scope.

### Phase 4: Transaction and Funds Features

Add withdrawals, deposits, fund transactions, convert, rewards, and internal transfers. Tests must not send real state-changing requests.

### Phase 5: M-Wallet

Add m-wallet public/private endpoints: index prices, limits, interest rates, loan, repayment, transfers, liquidations, interests, and AD ratio.

### Phase 6: WebSocket Gap Cleanup

Add WebSocket support for MWallet Pool Quota, Fast Trade, MWallet private channels, and book sequence/version fields.

## Acceptance Criteria

Before completing each phase, run at least:

```shell
poetry run ruff check .
poetry run pytest -v -s --cov=maicoin --cov-report=xml tests
```

REST private endpoint tests should use mocked transport/session objects. Do not use real API keys or send real order/withdrawal requests.
