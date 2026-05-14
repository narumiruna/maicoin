# Client Resilience and Ergonomics Plan

Status: **implemented and archived**.

This plan tracked production-readiness and ergonomics work for the REST v3 client and WebSocket stream. The client-resilience milestone is complete; remaining destructive live-test and dataclass-model ideas are tracked separately in `docs/plans/archived/client-resilience-and-ergonomics-follow-ups.md` and related archived plans.

## Implemented Scope

### WebSocket Production Resilience

Implemented in `src/maicoin/ws/stream.py`.

- `ReconnectPolicy` controls reconnect behavior, including max retries, base delay, max delay, and jitter.
- `Stream` can reconnect after non-cancellation disconnects and replay queued auth/subscription requests.
- Lifecycle callbacks are available for connection events:
  - `on_connected`
  - `on_disconnected`
  - `on_reconnecting`
  - `on_permanent_failure`
- `asyncio.CancelledError` is not swallowed, and the websocket is closed cleanly during cancellation.
- WebSocket connection options such as ping/timeout/queue settings can be passed through to the underlying connection factory.
- Tests simulate reconnects, disconnects, replayed subscriptions, and cancellation behavior in `tests/ws/test_stream.py`.

### Non-Blocking WebSocket Dispatch

Implemented in `src/maicoin/ws/stream.py`.

- Handlers may be synchronous or asynchronous callables.
- Dispatch modes are supported:
  - `inline`: backward-compatible, ordered handler execution.
  - `task`: schedule handler work with `asyncio.create_task()`.
  - `queue`: enqueue responses for consumer-managed processing.
- Handler exceptions are isolated through the configured error-handling path instead of unexpectedly killing normal receive-loop operation.
- Tests cover async handlers, task dispatch, queue dispatch, and handler error behavior.

### REST Retry and Rate-Limit Policy

Implemented in `src/maicoin/v3/client.py`.

- `RetryPolicy` controls retry attempts, backoff, max delay, jitter, retryable status codes, timeout/network retries, and `Retry-After` handling.
- Default behavior is conservative:
  - safe retries apply to idempotent methods such as `GET`.
  - non-idempotent requests are not retried unless explicitly enabled with `retry_non_idempotent=True`.
- Existing exception behavior is preserved after retry exhaustion.
- Tests cover retryable statuses, `Retry-After`, network failures, and non-idempotent retry gating in `tests/v3/test_client.py`.

### Async-First REST Client

Implemented in `src/maicoin/v3/client.py`.

- `Client` is async-first across the REST v3 surface.
- Public, authenticated read, and authenticated write methods are `async def` methods and use `httpx.AsyncClient` internally by default.
- `Client` supports async lifecycle management:

```python
async with Client(api_key="...", api_secret="...") as client:
    markets = await client.markets()
    accounts = await client.accounts()
```

- `await client.aclose()` is available for explicit cleanup.
- Explicit `_sync` convenience wrappers exist for synchronous scripts and applications.
- `_sync` wrappers have endpoint-specific signatures and return types for better IDE/type-checker support.
- `_sync` wrappers raise when called inside an already-running event loop; async applications such as FastAPI, Jupyter, and async bots should await async methods directly.
- Default sync-wrapper calls use fresh async sessions to avoid cross-event-loop reuse of the underlying `httpx.AsyncClient`.
- Tests have been converted toward native async style with `pytest.mark.anyio`.

### Pagination Helpers

Implemented in `src/maicoin/v3/client.py`.

- Async iterator helpers are available for historical/list workflows that have clear id/cursor progression semantics, including:
  - `iter_wallet_trades(...)`
  - `iter_order_history(...)`
- Iterators support page limits, `max_items`, and `max_pages` stop conditions.
- Tests cover cursor advancement, short-page termination, duplicate prevention, and max-page limits in `tests/v3/test_private.py`.

### Documentation and Examples

Implemented in `README.md` and examples.

- REST examples use async-first calls.
- Synchronous wrapper usage remains documented for simple scripts.
- Async lifecycle guidance covers `async with Client()`, `await client.aclose()`, and `_sync` wrapper limitations inside running event loops.
- README includes a FastAPI dependency example.

## Verification

- Client-resilience work landed via PR #62 / commit `1ae3b73 feat: add client resilience controls` and related prior PRs for async pagination, sync-wrapper lifecycle hardening, and sync-wrapper typing.
- Tests cover WebSocket reconnect/dispatch behavior, REST retries, async client methods, sync-wrapper safeguards, and async pagination iterators.
