# TODO

No outstanding implementation TODOs are currently tracked here.

## Completed Milestones

- REST v3 foundation, public endpoints, private order/trade/account endpoints, wallet funds, convert, and M-Wallet private endpoints.
- WebSocket public/private gap cleanup, including M-Wallet pool quota/private channels, book update ids, unsubscribe serialization, and string-preserving numeric payload fields.
- README REST v3 examples and official API documentation links in `AGENTS.md`.

## Verification

- `just` passed after Phase 7 WebSocket cleanup.
- Tests use mocked sessions/payloads and do not depend on real MAX API credentials.
