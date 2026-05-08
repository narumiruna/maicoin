# Live Integration Tests Plan

This document plans live integration tests for the MaiCoin MAX API. These tests call the real MAX API instead of using fake sessions or mocked payloads.

## Goals

- Verify that `maicoin.v3.Client` can connect to the real MAX REST v3 API.
- Verify that public endpoint responses can be parsed by the current Pydantic models.
- Verify that private read-only endpoints work with real authentication headers, signatures, nonces, and response models.
- Keep live tests isolated from normal unit tests so local development and CI are not affected by network access, API credentials, rate limits, or API availability.

## Non-goals

The first version will not test operations that change account state or introduce financial risk, such as:

- Creating or canceling orders
- Withdrawals
- Internal transfers
- Convert orders
- M-Wallet borrow, repay, or transfer operations

If these tests are added later, they must be treated as destructive tests and require an additional explicit opt-in environment variable.

## Test Categories

### Public live tests

These tests do not require API credentials and are the safest first milestone.

Recommended coverage:

- `Client().timestamp()`
- `Client().markets()`
- `Client().currencies()`
- `Client().ticker(market)`
- `Client().tickers([market])`
- `Client().depth(market, limit=1)`
- `Client().trades(market, limit=1)`
- `Client().kline(market, limit=1)`

Assertions should focus on stable behavior:

- The API is reachable and returns successfully.
- The payload can be parsed into typed client models.
- Tests do not assert fixed prices, volumes, or other market-dependent values.
- Tests only assert stable conditions such as market id, non-empty lists, timestamp types, and required fields.

### Private read-only live tests

These tests require `MAX_API_KEY` and `MAX_API_SECRET`, but must not change account state.

Recommended coverage:

- `client.info()`
- `client.accounts()`
- `client.open_orders(limit=1)`
- `client.closed_orders(limit=1)`
- `client.wallet_trades(limit=1)`

Assertions should verify that:

- Real API credentials can complete authenticated requests.
- Signatures and nonces are accepted by the real API.
- Private endpoint responses can be parsed into typed models.

If credentials are missing, private live tests should be skipped instead of failed.

### Destructive live tests

Do not implement these in the first version. If they are added later, they must use both markers:

- `@pytest.mark.live`
- `@pytest.mark.destructive`

They must also require an additional environment variable:

```shell
RUN_LIVE_TESTS=1 RUN_DESTRUCTIVE_TESTS=1 uv run pytest -m "live and destructive"
```

Every destructive test must include explicit risk controls, such as minimum order sizes, limit orders far away from the current market price, cleanup steps, and a manual recovery path if cleanup fails.

## Proposed File Structure

```text
tests/
  live/
    __init__.py
    conftest.py
    test_public_live.py
    test_private_readonly_live.py
```

`tests/live/conftest.py` should handle:

- Skipping `live` tests unless `RUN_LIVE_TESTS=1` is set.
- Providing a live market fixture.
- Providing an authenticated client fixture; private tests should skip when credentials are missing.

## Pytest Markers

Add the following to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
  "live: tests that call the real MaiCoin MAX API",
  "destructive: live tests that may change account state",
]
```

## Environment Variables

Recommended variables:

```dotenv
RUN_LIVE_TESTS=1
MAX_API_KEY=your_key
MAX_API_SECRET=your_secret
MAX_LIVE_MARKET=btctwd
RUN_DESTRUCTIVE_TESTS=0
```

Meanings:

- `RUN_LIVE_TESTS`: must be `1` to run live tests.
- `MAX_LIVE_MARKET`: market used by public tests; default can be `btctwd`.
- `MAX_API_KEY` / `MAX_API_SECRET`: required only for private read-only tests.
- `RUN_DESTRUCTIVE_TESTS`: reserved for future destructive tests; not used in the first version.

## Suggested Commands

Run all live tests manually:

```shell
RUN_LIVE_TESTS=1 uv run pytest -v -s -m live tests/live
```

Run only public live tests:

```shell
RUN_LIVE_TESTS=1 uv run pytest -v -s tests/live/test_public_live.py
```

Run private read-only live tests:

```shell
RUN_LIVE_TESTS=1 MAX_API_KEY=... MAX_API_SECRET=... uv run pytest -v -s tests/live/test_private_readonly_live.py
```

Optional `justfile` recipe:

```make
live-test:
    RUN_LIVE_TESTS=1 uv run pytest -v -s -m live tests/live
```

## CI Strategy

Live tests should not run in default CI.

If GitHub Actions support is added later:

- Use `workflow_dispatch` for manual triggering.
- Read `MAX_API_KEY` and `MAX_API_SECRET` from GitHub Secrets.
- Do not run destructive tests in CI unless there is a stricter manual approval process.

## Implementation Order

1. Register the `live` and `destructive` markers in `pyproject.toml`.
2. Create `tests/live/` with shared fixtures and skip logic.
3. Implement public live tests.
4. Add a `just live-test` recipe.
5. Implement private read-only live tests.
6. Update `README.md` with a short section explaining how to run live integration tests.
7. Leave destructive tests for a separate design pass.

## Notes

- Live tests must not depend on fixed market prices or fixed account balances.
- Live tests can fail because of network issues, MAX API maintenance, rate limits, or account permissions.
- Private tests must remain read-only. Any state-changing behavior requires a separate marker and a second opt-in environment variable.
- When endpoint behavior needs confirmation, prefer the official REST v3 documentation and OpenAPI JSON. The MAX v3 OpenAPI JSON is available at `https://max-api.maicoin.com/api/doc/external/v3`.
