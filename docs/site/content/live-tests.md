# 🧪 Live integration tests

Live tests call the real MAX API instead of using fake sessions or mocked payloads. They are skipped unless explicitly enabled, so the default test run is hermetic.

## Run them

```shell
RUN_LIVE_TESTS=1 uv run pytest -v -s -m live tests/live
# or, with credentials loaded from .env
just live-test
```

## Categories

- **Public** — read-only tests against `Client().timestamp()`, `markets()`, `currencies()`, `ticker(...)`, `depth(...)`, `trades(...)`, `kline(...)`. No credentials required.
- **Private read-only** — `Client.info()`, `accounts()`, `open_orders()`, `closed_orders()`, `wallet_trades()`. Skipped automatically when `MAX_API_KEY` / `MAX_API_SECRET` are missing.
- **Destructive** — placing/cancelling orders, transfers, withdrawals, borrow/repay. These tests must be marked with both `live` and `destructive`, require `RUN_LIVE_TESTS=1` plus `RUN_DESTRUCTIVE_TESTS=1`, and must follow the archived safety design before implementation.

## Environment variables

```dotenv
RUN_LIVE_TESTS=1
RUN_DESTRUCTIVE_TESTS=1  # only for reviewed destructive tests
MAX_API_KEY=your_key
MAX_API_SECRET=your_secret
MAX_LIVE_MARKET=btctwd   # optional override of the default public test market
```

Destructive tests need additional test-specific limits, such as an allowlisted market, a maximum notional amount, and enough available balance for setup and cleanup. Do not add a destructive test that can run from the normal `just` or `just test` path.

## What they assert

Live tests are written to be stable across market conditions:

- The API is reachable and returns a 2xx response.
- The payload parses into the typed Pydantic models.
- Only stable invariants are asserted (market id, non-empty lists, timestamp types, required fields). They never assert fixed prices, balances, or volumes.

## CI

Live tests do **not** run in default CI. The archived plan ([live-integration-tests-plan](https://github.com/narumiruna/maicoin/blob/main/docs/plans/archived/live-integration-tests-plan.md)) sketches a future `workflow_dispatch`-triggered job that reads credentials from GitHub Secrets. Destructive test controls are tracked separately in [destructive-live-test-safety](https://github.com/narumiruna/maicoin/blob/main/docs/plans/archived/destructive-live-test-safety.md).
