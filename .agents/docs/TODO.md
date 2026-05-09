# TODO

## Live Integration Tests

Plan archived: [`archived/live-integration-tests-plan.md`](archived/live-integration-tests-plan.md). Read-only public and private live tests are implemented; destructive live tests remain intentionally out of scope until a separate design pass.

## Client Resilience and Ergonomics

Plan: [`plans/client-resilience-and-ergonomics-plan.md`](plans/client-resilience-and-ergonomics-plan.md)

- [ ] Add WebSocket reconnect, heartbeat configuration, graceful cancellation, and non-blocking handler dispatch.
- [ ] Add conservative REST retry/rate-limit support.
- [x] Add pagination helpers for historical/list endpoints.
- [x] Migrate REST `Client` to async-first methods with explicit `_sync` convenience wrappers.
- [x] Harden `_sync` wrapper lifecycle after async-first migration; avoid or document cross-event-loop reuse of the underlying `httpx.AsyncClient`.
- [x] Replace generic `_sync` wrapper signatures with endpoint-specific parameters and return types for better IDE/type-checker support.
- [x] Convert REST client tests toward native async style (`pytest.mark.anyio`) instead of relying mostly on `asyncio.run()` / `_sync` wrappers.
- [x] Add async pagination helpers / async iterators for historical and list endpoints, for example `async for order in client.iter_order_history(...)`.
- [x] Expand async lifecycle docs and examples, including `async with Client()`, `await client.aclose()`, `_sync` limitations in existing event loops, and a FastAPI dependency example.

## Completed Milestones

- REST v3 foundation, public endpoints, private order/trade/account endpoints, wallet funds, convert, and M-Wallet private endpoints.
- WebSocket public/private gap cleanup, including M-Wallet pool quota/private channels, book update ids, unsubscribe serialization, and string-preserving numeric payload fields.
- README REST v3 examples and official API documentation links in `AGENTS.md`.
- Live integration tests plan documented in `docs/live-integration-tests-plan.md`.

## Verification

- `just` passed after Phase 7 WebSocket cleanup.
- Tests currently use mocked sessions/payloads and do not depend on real MAX API credentials.
- Read-only live integration tests are implemented; destructive live tests are still intentionally gated for a future design.
