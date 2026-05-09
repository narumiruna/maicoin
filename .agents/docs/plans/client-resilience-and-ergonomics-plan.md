# Client Resilience and Ergonomics Plan

## Review of Reported Gaps

Overall, the review is directionally correct. The current package has broad endpoint coverage, but several production-readiness and ergonomics gaps remain.

1. **Async REST client: valid, but not urgent for all users.** `src/maicoin/v3/client.py` is synchronous and uses `httpx.Client`. Async users currently need a thread pool or must call `Client.request()` through their own async wrapper. Because the dependency is already `httpx`, an `AsyncClient` is feasible, but it doubles the public client surface unless the request-building/parsing logic is shared carefully.
2. **WebSocket reconnect / heartbeat / recovery: valid and high impact.** `Stream.arun()` opens one connection and raises on disconnect. It does not implement reconnect backoff, resubscription after reconnect, explicit ping/heartbeat configuration, graceful cancellation, or error callbacks.
3. **WebSocket handlers block the receive loop: valid and high impact.** Handlers are called inline with `handler(resp)`. A slow handler delays `ws.recv()` and can cause dropped/late messages. The stream should support async handlers and/or queue-based dispatch.
4. **Rate-limit / retry support: valid, but should be conservative.** REST errors currently raise immediately after a single request. There is no `Retry-After` support, timeout retry, or backoff for 429/502/503/504. Automatic retries must be opt-in or limited to safe/idempotent methods unless callers explicitly enable retries for private write endpoints.
5. **Pagination helpers: valid.** Methods such as `closed_orders()`, `wallet_trades()`, `order_history()`, deposits, withdrawals, transfers, and M-Wallet list endpoints expose cursor/timestamp/from_id/limit parameters, but users must write pagination loops themselves.
6. **Destructive live tests: valid but lower priority.** Read-only live tests exist. Destructive tests still need a separate safety design because they can place/cancel orders or mutate account state.
7. **Dataclass low-level models: already planned, but should be lower priority.** A plan exists, but benchmark memory showed Pydantic v2 is currently faster than the manual dataclass parsers tested so far. Treat this as an experimental, benchmark-driven optimization, not an urgent performance fix.

## Recommended Priority Order

### Priority 1: WebSocket Production Resilience

Goal: make `Stream` stable enough for long-running processes.

Planned changes:

- Add configurable reconnect policy:
  - `reconnect: bool = True`
  - `max_retries: int | None = None`
  - `base_delay`, `max_delay`, jitter
- Re-send queued auth/subscription requests after reconnect.
- Add callbacks or handler events for connection lifecycle:
  - connected
  - disconnected
  - reconnecting
  - permanent failure
- Support graceful cancellation:
  - do not swallow `asyncio.CancelledError`
  - close websocket cleanly on cancellation
- Expose `websockets.connect()` options such as `ping_interval`, `ping_timeout`, `close_timeout`, and maybe `max_queue`.
- Add unit tests with a fake websocket/connect factory that simulates disconnects and verifies resubscription/backoff behavior.

### Priority 2: Non-Blocking WebSocket Dispatch

Goal: avoid blocking the receive loop when handlers are slow.

Planned changes:

- Type handlers as sync or async callables accepting `Response`.
- Detect awaitables and support `async def` handlers.
- Add dispatch modes:
  - `inline`: current behavior, backwards compatible
  - `task`: schedule each handler with `asyncio.create_task()`
  - `queue`: push responses to an `asyncio.Queue` for consumer-managed processing
- Add error handling for handler exceptions so one bad handler does not kill the stream unless configured.
- Document ordering trade-offs: inline preserves strict order; task mode may not; queue mode gives user control.

### Priority 3: REST Retry and Rate-Limit Policy

Goal: reduce transient failures without hiding important API errors.

Planned changes:

- Add a small `RetryPolicy` dataclass:
  - enabled
  - total attempts
  - backoff factor / max delay / jitter
  - retry status codes: default `429, 502, 503, 504`
  - retry timeout/network exceptions
  - respect `Retry-After` when present
- Default to conservative behavior:
  - safe retries for `GET`
  - no automatic retry for private write methods unless explicitly enabled
- Preserve current exceptions after retry exhaustion.
- Add tests for 429 with `Retry-After`, 503 backoff, timeout retry, and no retry on non-idempotent POST by default.

### Priority 4: Pagination Helpers

Goal: make common historical data access easier and less error-prone.

Planned changes:

- Add iterator helpers such as:
  - `iter_wallet_trades(...)`
  - `iter_closed_orders(...)`
  - `iter_order_history(...)`
  - `iter_deposits(...)`
  - `iter_withdrawals(...)`
  - `iter_m_wallet_*` for list endpoints with compatible pagination fields
- Keep existing list-returning methods unchanged.
- Start with endpoints that use `from_id` or timestamp/order semantics clearly documented by MAX.
- Stop conditions:
  - empty page
  - page smaller than limit
  - caller-provided `max_items` / `max_pages`
- Add tests for parameter progression and duplicate prevention.

### Priority 5: Async REST Client

Goal: support FastAPI, asyncio bots, and async services natively.

Planned changes:

- Add `AsyncClient` using `httpx.AsyncClient` and an async session protocol.
- Share request construction, auth signing, error handling, and model parsing with the sync client where practical.
- Support async context manager lifecycle:

```python
async with AsyncClient(api_key="...", api_secret="...") as client:
    ticker = await client.ticker("btctwd")
```

- Keep sync `Client` backwards compatible.
- Add tests using a fake async session, plus type checks for public methods.

### Priority 6: Destructive Live Tests

Goal: safely test order placement/cancellation and other mutating endpoints.

Planned changes:

- Keep destructive tests opt-in behind a separate environment flag such as `RUN_DESTRUCTIVE_LIVE_TESTS=1`.
- Require explicit market/currency env vars and minimum balance checks.
- Use far-from-market limit orders where possible.
- Always attempt cleanup and document manual recovery steps.
- Do not run destructive tests in normal CI.

### Priority 7: Dataclass Low-Level Models

Goal: only continue if benchmark evidence shows value or if users need a low-level payload-shaped API.

Planned changes:

- Keep the existing dataclass plan in `.agents/docs/plans/dataclass-low-level-models-plan.md`.
- Re-run benchmarks before implementation.
- Preserve transport-specific raw models and normalized domain models as separate layers.
- Avoid replacing Pydantic unless there is a measured benefit and a compatibility migration path.

## Acceptance Criteria

- Existing public API remains backwards compatible.
- New features are opt-in where behavior could surprise users.
- Unit tests cover failure paths, cancellation, retries, and pagination edge cases.
- Documentation explains when to use sync REST, async REST, inline WebSocket handlers, task dispatch, and queue dispatch.
