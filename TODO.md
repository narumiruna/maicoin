# TODO.md

## Priority Conclusion

The main missing area is **REST API v3**. The repository currently has broad WebSocket support, but REST support only contains `maicoin/v2/kline.py` for `GET /api/v2/k`. The official v3 endpoints, authentication flow, client abstraction, models, and tests still need to be implemented.

## Phase 1: Build the v3 Foundation

- [x] Add `maicoin/v3/__init__.py`.
- [x] Add `maicoin/v3/auth.py`.
  - [x] Generate nonce values.
  - [x] Build payload content with `nonce`, request params, and `path`.
  - [x] JSON-stringify and Base64-encode the payload.
  - [x] Generate an HMAC-SHA256 hex signature.
  - [x] Generate `X-MAX-ACCESSKEY`, `X-MAX-PAYLOAD`, and `X-MAX-SIGNATURE` headers.
- [x] Add `maicoin/v3/client.py`.
  - [x] Set `BASE_URL = "https://max-api.maicoin.com"`.
  - [x] Set a default timeout.
  - [x] Support GET query params.
  - [x] Support POST/DELETE/PUT JSON bodies.
  - [x] Support public and private requests.
- [x] Add `maicoin/v3/errors.py`.
  - [x] Handle HTTP status errors.
  - [x] Handle MAX API error responses.
- [x] Add auth and client unit tests.
  - [x] Test signatures with a fixed nonce.
  - [x] Test GET params are sent as query params.
  - [x] Test POST/DELETE params are sent as JSON bodies.

## Phase 2: REST v3 Public Endpoints

- [ ] `GET /api/v3/markets`: all available markets.
- [ ] `GET /api/v3/currencies`: currencies.
- [ ] `GET /api/v3/timestamp`: server timestamp.
- [ ] `GET /api/v3/k`: K-lines; replace or align with the existing v2 `KLineRequest`.
- [ ] `GET /api/v3/depth`: order book depth.
- [ ] `GET /api/v3/trades`: public trades.
- [ ] `GET /api/v3/tickers`: all tickers.
- [ ] `GET /api/v3/ticker`: single ticker.
- [ ] `GET /api/v3/wallet/m/index_prices`: m-wallet index prices.
- [ ] `GET /api/v3/wallet/m/historical_index_prices`: historical index prices.
- [ ] `GET /api/v3/wallet/m/limits`: available loan amount.
- [ ] `GET /api/v3/wallet/m/interest_rates`: interest rates.
- [ ] Add request construction tests for the endpoints above.
- [ ] Add Pydantic parsing tests for common responses.

## Phase 3: REST v3 Order, Trade, and Account

- [ ] `GET /api/v3/info`: user info.
- [ ] `GET /api/v3/wallet/{path_wallet_type}/accounts`: wallet balances.
- [ ] `GET /api/v3/wallet/{path_wallet_type}/trades`: trade history.
- [ ] `GET /api/v3/wallet/{path_wallet_type}/orders/open`: open orders.
- [ ] `GET /api/v3/wallet/{path_wallet_type}/orders/closed`: closed orders.
- [ ] `GET /api/v3/wallet/{path_wallet_type}/orders/history`: order history by order id.
- [ ] `POST /api/v3/wallet/{path_wallet_type}/order`: submit a sell/buy order.
- [ ] `DELETE /api/v3/wallet/{path_wallet_type}/orders`: cancel all orders.
- [ ] `GET /api/v3/order`: order detail.
- [ ] `DELETE /api/v3/order`: cancel one order.
- [ ] `GET /api/v3/order/trades`: order trade detail.
- [ ] Add order side/type/state enums.
- [ ] Add create/cancel order tests using mocks only; do not send real trading requests.

## Phase 4: REST v3 Transaction and Wallet Funds

- [ ] `GET /api/v3/withdrawal`: withdrawal detail.
- [ ] `POST /api/v3/withdrawal`: crypto withdrawal.
- [ ] `POST /api/v3/withdrawal/twd`: TWD withdrawal.
- [ ] `GET /api/v3/withdrawals`: withdrawal list.
- [ ] `GET /api/v3/withdraw_addresses`: withdraw addresses.
- [ ] `GET /api/v3/deposit`: deposit detail.
- [ ] `GET /api/v3/deposits`: deposit list.
- [ ] `GET /api/v3/deposit_address`: deposit address by currency/version.
- [ ] `GET /api/v3/internal_transfers`: internal transfers.
- [ ] `GET /api/v3/rewards`: rewards.
- [ ] `GET /api/v3/fund_transactions/deposits`.
- [ ] `GET /api/v3/fund_transactions/deposit`.
- [ ] `GET /api/v3/fund_transactions/withdrawals`.
- [ ] `GET /api/v3/fund_transactions/withdrawal`.
- [ ] `GET /api/v3/fund_transactions/transfers`.
- [ ] `GET /api/v3/fund_transactions/transfer`.

## Phase 5: REST v3 Convert

- [ ] `POST /api/v3/convert`: create convert.
- [ ] `GET /api/v3/convert`: convert detail.
- [ ] `GET /api/v3/converts`: convert list.
- [ ] Add convert request/response models.
- [ ] Add mocked tests.

## Phase 6: REST v3 M-Wallet Private Endpoints

- [ ] `POST /api/v3/wallet/m/loan`: submit loan.
- [ ] `GET /api/v3/wallet/m/loans`: loan history.
- [ ] `POST /api/v3/wallet/m/transfer`: spot wallet to/from m-wallet transfer.
- [ ] `GET /api/v3/wallet/m/transfers`: m-wallet transfer history.
- [ ] `POST /api/v3/wallet/m/repayment`: submit repayment.
- [ ] `GET /api/v3/wallet/m/repayments`: repayment history.
- [ ] `GET /api/v3/wallet/m/liquidations`: liquidation history.
- [ ] `GET /api/v3/wallet/m/liquidation`: liquidation detail.
- [ ] `GET /api/v3/wallet/m/interests`: interest history.
- [ ] `GET /api/v3/wallet/m/ad_ratio`: latest AD ratio.

## Phase 7: WebSocket Gap Cleanup

- [ ] Add public channel support for MWallet Pool Quota.
- [ ] Add private channel support for Fast Trade.
- [ ] Add MWallet private channels: order, trade, fast trade, account, AD ratio, and borrowing.
- [ ] Add book response fields: `fi`, `li`, and `v`.
- [ ] Add a `market_status` subscription test.
- [ ] Check whether `Request.unsubscribe()` serialization should support the documentation's `subscription` versus `subscriptions` difference.
- [ ] Check whether timestamp, price, and volume fields should preserve string precision instead of always converting to float.

## Documentation

- [x] Update `README.md` so the HTTP API link points to v3.
- [x] Add a REST v3 public client example to README.
- [x] Add a REST v3 private auth example to README without real keys.
- [ ] Keep official documentation links in `AGENTS.md`:
  - [ ] https://max-api.maicoin.com/doc/v3.html
  - [ ] https://maicoin.github.io/max-websocket-docs/

## Quality Gate

- [ ] `poetry run ruff check .`
- [ ] `poetry run pytest -v -s --cov=maicoin --cov-report=xml tests`
- [ ] Confirm tests do not depend on real MAX API credentials.
- [ ] Confirm `.env`, API keys, secrets, payloads, and signature logs are not committed.
