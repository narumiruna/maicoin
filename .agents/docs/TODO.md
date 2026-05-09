# TODO

## Active Follow-Ups

Follow-up plan: [`plans/client-resilience-and-ergonomics-follow-ups.md`](plans/client-resilience-and-ergonomics-follow-ups.md)

### Destructive Live Tests

Plan archived: [`archived/live-integration-tests-plan.md`](archived/live-integration-tests-plan.md). Read-only public and private live tests are implemented; destructive live tests remain intentionally out of scope until a separate safety design pass.

- [ ] Design opt-in destructive live tests with explicit environment gates, balance checks, cleanup, and manual recovery steps.

### Dataclass Low-Level Model Experiment

Plan archived: [`archived/dataclass-low-level-models-plan.md`](archived/dataclass-low-level-models-plan.md).

- [ ] Revisit low-level dataclass models only if fresh benchmark evidence shows value and there is a compatibility migration path.

## Completed Milestones

### Client Resilience and Ergonomics

Archived plan: [`archived/completed-client-resilience-and-ergonomics-plan.md`](archived/completed-client-resilience-and-ergonomics-plan.md)

- [x] Add WebSocket reconnect, heartbeat configuration, graceful cancellation, and non-blocking handler dispatch.
- [x] Add conservative REST retry/rate-limit support.
- [x] Add pagination helpers for historical/list endpoints.
- [x] Migrate REST `Client` to async-first methods with explicit `_sync` convenience wrappers.
- [x] Harden `_sync` wrapper lifecycle after async-first migration; avoid cross-event-loop reuse of the underlying `httpx.AsyncClient`.
- [x] Replace generic `_sync` wrapper signatures with endpoint-specific parameters and return types for better IDE/type-checker support.
- [x] Convert REST client tests toward native async style (`pytest.mark.anyio`) instead of relying mostly on `asyncio.run()` / `_sync` wrappers.
- [x] Add async pagination helpers / async iterators for historical and list endpoints, for example `async for order in client.iter_order_history(...)`.
- [x] Expand async lifecycle docs and examples, including `async with Client()`, `await client.aclose()`, `_sync` limitations in existing event loops, and a FastAPI dependency example.

### REST v3 and WebSocket API Coverage

- [x] REST v3 foundation, public endpoints, private order/trade/account endpoints, wallet funds, convert, and M-Wallet private endpoints.
- [x] WebSocket public/private gap cleanup, including M-Wallet pool quota/private channels, book update ids, unsubscribe serialization, and string-preserving numeric payload fields.
- [x] README REST v3 examples and official API documentation links in `AGENTS.md`.
- [x] Read-only live integration tests.

## Verification

- Client resilience and ergonomics landed via PR #62 / commit `1ae3b73 feat: add client resilience controls` and related prior PRs.
- Tests use mocked sessions/payloads for normal runs and do not depend on real MAX API credentials.
- Read-only live integration tests are implemented; destructive live tests are still intentionally gated for a future design.
