# Destructive live-test safety design

Date: 2026-05-15 (Asia/Taipei)

Destructive live tests are tests that can change real account state: order placement/cancellation, transfers, withdrawals, convert orders, M-Wallet borrow/repay/transfer, or any future endpoint with equivalent risk.

## Opt-in gates

Every destructive live test must:

- Use both `@pytest.mark.live` and `@pytest.mark.destructive`.
- Stay skipped unless `RUN_LIVE_TESTS=1` and `RUN_DESTRUCTIVE_TESTS=1` are both set.
- Require `MAX_API_KEY` and `MAX_API_SECRET`.
- Require test-specific safety variables instead of hard-coded markets or amounts.

Suggested safety variables:

```dotenv
MAX_DESTRUCTIVE_MARKET=btctwd
MAX_DESTRUCTIVE_BASE_CURRENCY=btc
MAX_DESTRUCTIVE_QUOTE_CURRENCY=twd
MAX_DESTRUCTIVE_MAX_NOTIONAL_TWD=100
MAX_DESTRUCTIVE_CLIENT_OID_PREFIX=maicoin-live-test
```

## Balance and limit checks

Before submitting a state-changing request, the test must:

- Fetch accounts with the same client that will submit the request.
- Verify available balance is enough for setup and cleanup.
- Verify the intended notional amount is at or below the configured maximum.
- Verify the market/currency is explicitly allowlisted by environment variable.
- Skip, not fail, when balances or limits are insufficient.

## Cleanup

Each test must own a unique local identifier, such as a `client_oid` with `MAX_DESTRUCTIVE_CLIENT_OID_PREFIX`.

Cleanup requirements:

- Cancel any order created by the test by exact `client_oid` or order id.
- Re-read state after cleanup and assert no matching open order remains.
- Never call broad cancellation APIs without exact filters.
- Keep cleanup in `try` / `finally` so it runs when assertions fail.

Transfers, withdrawals, and borrow/repay tests need a separate cleanup design before implementation. Do not add them just because the marker gates exist.

## Manual recovery

Every destructive test file must include a short module docstring or comment with:

- The endpoint under test.
- The environment variables required to run it.
- How to find created resources by `client_oid`, order id, or transfer/withdrawal id.
- The manual cleanup action if automatic cleanup fails.

## CI policy

Do not run destructive live tests in default CI. A future manual `workflow_dispatch` job may expose them only when:

- The job environment has protected secrets.
- The workflow input names the target market/currency.
- The workflow logs print the configured maximum notional amount before running tests.
