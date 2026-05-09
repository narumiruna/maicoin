# TODO

## Live Integration Tests

Plan archived: [`archived/live-integration-tests-plan.md`](archived/live-integration-tests-plan.md). Read-only public and private live tests are implemented; destructive live tests remain intentionally out of scope until a separate design pass.

## Client Resilience and Ergonomics

Plan: [`plans/client-resilience-and-ergonomics-plan.md`](plans/client-resilience-and-ergonomics-plan.md)

- [ ] Add WebSocket reconnect, heartbeat configuration, graceful cancellation, and non-blocking handler dispatch.
- [ ] Add conservative REST retry/rate-limit support.
- [ ] Add pagination helpers for historical/list endpoints.
- [ ] Add an async REST client.

## Dataclass Low-Level Models

Plan: [`plans/dataclass-low-level-models-plan.md`](plans/dataclass-low-level-models-plan.md)

- [ ] Re-evaluate a dataclass data layer with benchmarks before implementation while keeping Pydantic as the high-level validated API.

## Completed Milestones

- REST v3 foundation, public endpoints, private order/trade/account endpoints, wallet funds, convert, and M-Wallet private endpoints.
- WebSocket public/private gap cleanup, including M-Wallet pool quota/private channels, book update ids, unsubscribe serialization, and string-preserving numeric payload fields.
- README REST v3 examples and official API documentation links in `AGENTS.md`.
- Live integration tests plan documented in `docs/live-integration-tests-plan.md`.

## Verification

- `just` passed after Phase 7 WebSocket cleanup.
- Tests currently use mocked sessions/payloads and do not depend on real MAX API credentials.
- Read-only live integration tests are implemented; destructive live tests are still intentionally gated for a future design.
