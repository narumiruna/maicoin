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
- **Destructive** — placing/cancelling orders, transfers, withdrawals, borrow/repay. Intentionally **not implemented** in the first pass; will require a separate `RUN_DESTRUCTIVE_TESTS=1` opt-in and risk controls.

## Environment variables

```dotenv
RUN_LIVE_TESTS=1
MAX_API_KEY=your_key
MAX_API_SECRET=your_secret
MAX_LIVE_MARKET=btctwd   # optional override of the default public test market
```

## What they assert

Live tests are written to be stable across market conditions:

- The API is reachable and returns a 2xx response.
- The payload parses into the typed Pydantic models.
- Only stable invariants are asserted (market id, non-empty lists, timestamp types, required fields). They never assert fixed prices, balances, or volumes.

## CI

Live tests do **not** run in default CI. The archived plan ([live-integration-tests-plan](https://github.com/narumiruna/maicoin/blob/main/docs/archived/live-integration-tests-plan.md)) sketches a future `workflow_dispatch`-triggered job that reads credentials from GitHub Secrets.
