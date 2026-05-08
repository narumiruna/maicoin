# TODO

## Live Integration Tests

Plan: [`docs/live-integration-tests-plan.md`](live-integration-tests-plan.md)

- [ ] Register `live` and `destructive` pytest markers in `pyproject.toml`.
- [ ] Create `tests/live/` with shared fixtures and skip logic.
- [ ] Implement public live tests for read-only MAX REST v3 public endpoints.
- [ ] Add a `just live-test` recipe.
- [ ] Implement private read-only live tests that use `MAX_API_KEY` and `MAX_API_SECRET` when available.
- [ ] Update `README.md` with a short section explaining how to run live integration tests.
- [ ] Leave destructive live tests for a separate design pass; do not include them in the first implementation.

## Completed Milestones

- REST v3 foundation, public endpoints, private order/trade/account endpoints, wallet funds, convert, and M-Wallet private endpoints.
- WebSocket public/private gap cleanup, including M-Wallet pool quota/private channels, book update ids, unsubscribe serialization, and string-preserving numeric payload fields.
- README REST v3 examples and official API documentation links in `AGENTS.md`.
- Live integration tests plan documented in `docs/live-integration-tests-plan.md`.

## Verification

- `just` passed after Phase 7 WebSocket cleanup.
- Tests currently use mocked sessions/payloads and do not depend on real MAX API credentials.
- Live integration tests are planned but not yet implemented.
