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

### Priority 5: Async-First REST Client

Goal: support FastAPI, asyncio bots, and async services natively while keeping a simple sync convenience layer.

Preferred design:

- Make `Client` async-first instead of adding a separate `AsyncClient` class.
- Convert the whole typed REST surface to async methods, not just selected endpoints. Examples:

```python
async with Client(api_key="...", api_secret="...") as client:
    markets = await client.markets()
    currencies = await client.currencies()
    ticker = await client.ticker("btctwd")
    accounts = await client.accounts()
```

- Apply the same async-first rule to public endpoints, authenticated read endpoints, and authenticated write endpoints such as order creation/cancellation.
- Use `httpx.AsyncClient` and an async session protocol internally.
- Add sync convenience wrappers with an explicit `_sync` suffix for the whole REST surface:

```python
def currencies_sync(self) -> list[Currency]:
    return asyncio.run(self.currencies())
```

- For every async method that should remain callable from synchronous scripts, provide the matching `_sync` wrapper, for example `markets_sync()`, `ticker_sync(...)`, `accounts_sync()`, and `create_order_sync(...)`.
- Treat `_sync` wrappers as convenience APIs for scripts and synchronous applications, not for code already running inside an event loop. Document that `asyncio.run()` raises when called from an existing event loop, so FastAPI/Jupyter/async bot users should call the async methods directly.
- Preserve request construction, auth signing, nonce injection, error handling, and model parsing behavior while changing the transport to async.
- Because this changes existing `Client` method call semantics from `client.currencies()` to `await client.currencies()`, plan it as a breaking API change or provide a migration window with deprecation warnings if backwards compatibility is required.
- Add tests using a fake async session, tests for `_sync` wrappers, and type checks for async public methods.

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

- Existing public API remains backwards compatible except for explicitly planned breaking changes such as an async-first REST client migration.
- New behavior is opt-in where it could surprise users, or documented as part of a deliberate migration path.
- Unit tests cover failure paths, cancellation, retries, and pagination edge cases.
- Documentation explains when to use async REST methods, `_sync` REST wrappers, inline WebSocket handlers, task dispatch, and queue dispatch.
