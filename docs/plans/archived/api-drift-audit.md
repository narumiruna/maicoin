# MAX API drift audit

Date: 2026-05-15 (Asia/Taipei)

Sources:

- REST v3 documentation: <https://max-api.maicoin.com/doc/v3.html>
- REST v3 OpenAPI document: <https://max-api.maicoin.com/api/doc/external/v3>
- WebSocket documentation: <https://maicoin.github.io/max-websocket-docs/>

## Summary

The REST v3 client route surface matches the official OpenAPI path surface as of this audit. The WebSocket models covered the current response events, but the outbound auth filter surface was missing the official `fast_trade_update` filter and the guide showed private events as nonexistent subscription channels.

Both WebSocket issues were fixed in this pass.

## REST v3 coverage

The official REST OpenAPI document was compared against `EndpointSpec` declarations under `src/maicoin/v3/_endpoints/`.

Covered route families:

- Public market data: markets, currencies, timestamp, kline, depth, trades, ticker, tickers.
- User and order history: info, accounts, wallet trades, open/closed/history orders, single order, order trades.
- Order intake: create order, cancel order, bulk cancel.
- Funds: withdrawals, withdrawal addresses, deposits, deposit address, internal transfers, rewards, fund transactions.
- Convert: create convert, single convert, convert history.
- M-Wallet: index prices, historical index prices, limits, interest rates, loans, transfers, repayments, liquidations, interests, ad ratio.

No missing REST path was found. The `deposit_address` route from the official changelog is already represented by `DEPOSIT_ADDRESS`.

Remaining REST watch points:

- Keep raw dict return types for endpoints whose official shape is a currency/market keyed mapping until there is a stable typed model that improves readability.
- If future endpoint-family modules start duplicating response parsing boilerplate, revisit endpoint declarations that combine route metadata with response shape.

## WebSocket coverage

The official WebSocket docs were compared against `Channel`, `Filter`, `Event`, `Response`, and the request/subscription tests.

Covered public subscription channels:

- `book`
- `trade`
- `ticker`
- `kline`
- `market_status`
- `pool_quota`

Covered private response events include order, trade, fast trade, account, M-Wallet order/trade/fast trade/account, ad ratio, and borrowing snapshots/updates.

Drift found:

| Priority | Area | Finding | Resolution |
| --- | --- | --- | --- |
| P0 | WebSocket auth filters | Official docs support `fast_trade_update`, but `Filter` did not. | Added `Filter.FAST_TRADE_UPDATE` and request serialization coverage. |
| P1 | WebSocket private setup | Docs used nonexistent `Channel.ORDER`, `Channel.TRADE_UPDATE`, and `Channel.BALANCE_UPDATE`. Private events are selected by auth filters. | Updated docs/examples to use `Stream.from_env(auth_filters=[...])`. |
| P1 | WebSocket ergonomics | `Request.auth()` could parse filters, but `Stream` could not request them directly. | Added `auth_filters` to `Stream`, `Stream.from_env()`, and `Stream.auth()`. |

No remaining high-priority API drift is known after these fixes.
