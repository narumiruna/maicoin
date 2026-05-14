# Codebase Architecture Deepening Opportunities

Status: **archived after completing the actionable first pass**.

Completion note: the REST v3 test harness, REST v3 model locality, WebSocket Stream lifecycle split, and public export/docs-reference consistency check are complete. Remaining speculative candidates stay in `docs/plans/TODO.md` until there is a concrete trigger.

This plan captures architecture deepening candidates found during the May 2026 codebase review. It is intentionally a planning document: do not implement every item at once. Pick one candidate, sharpen the intended Module Interface, then make a focused change with tests.

## Context

No project `CONTEXT.md` or `docs/adr/` files existed when this review was written, so this plan uses domain language already present in the codebase: REST v3, Order, funds, Convert, M-Wallet, WebSocket Stream, Response, and Subscription.

Recent REST v3 work already deepened endpoint locality:

- `Client` keeps its public Interface stable.
- Endpoint request metadata and response parsing moved into `src/maicoin/v3/_endpoints/` family modules.
- `EndpointSpec` and `EndpointExecutor` centralize method/path/auth metadata, parameter omission, and common model/list/mapping parsing.

Future work should preserve that direction: make Modules deeper, keep public Interfaces stable unless a breaking change is explicitly planned, and use tests at the same seam callers use.

## Candidate 1: Deepen REST v3 model locality

### Files

- `src/maicoin/v3/models.py`
- `src/maicoin/v3/__init__.py`
- `src/maicoin/v3/_endpoints/*.py`
- `tests/v3/*`

### Problem

REST v3 endpoint request and parse rules are now organized by domain family, but raw Pydantic models are still concentrated in one large `models.py` Module. Public market data, Order intake/history, funds, Convert, M-Wallet, and shared enums all share the same file.

That weakens locality: a M-Wallet drift requires jumping between `_endpoints/m_wallet.py` and unrelated models in `models.py`; funds drift has the same problem. The raw model Module is valuable, but its Interface is too broad for the new endpoint-family structure.

### Solution

Split REST v3 raw models by domain family while preserving public imports from `maicoin.v3`:

- `src/maicoin/v3/models/base.py` for `MaxBaseModel` and shared config.
- `src/maicoin/v3/models/public_market_data.py` for markets, currencies, kline, depth, trades, tickers, timestamp.
- `src/maicoin/v3/models/orders.py` for accounts, Order, Order enums, private trades, user info.
- `src/maicoin/v3/models/funds.py` for withdrawals, deposits, fund transactions, rewards, internal transfers.
- `src/maicoin/v3/models/convert.py` for Convert models.
- `src/maicoin/v3/models/m_wallet.py` for M-Wallet models.

Keep `src/maicoin/v3/models.py` as a compatibility re-export shim, or migrate to a package only if import compatibility is deliberately handled.

### Benefits

- **Locality**: endpoint rules and payload schemas for the same domain live near each other.
- **Leverage**: adding a new endpoint family means following an existing family pattern for specs, parsers, models, and tests.
- Tests can mirror the domain family more clearly and locate schema failures faster.

### Test surface

- Existing `tests/v3/*` should continue to pass unchanged where possible.
- Add focused import compatibility tests for `from maicoin.v3.models import ...` and `from maicoin.v3 import ...`.
- Run `just` and `just docs-build`.

## Candidate 2: Deepen WebSocket Stream lifecycle

### Files

- `src/maicoin/ws/stream.py`
- `tests/ws/test_stream.py`
- `docs/websocket.md`

### Problem

`Stream` currently mixes several responsibilities in one implementation:

- request queue, auth, and subscription replay
- websocket connect factory and connect options
- reconnect policy, retry count, and sleep
- lifecycle callback ordering
- raw message receive
- `Response.model_validate_json(...)`
- dispatch modes: `inline`, `task`, and `queue`
- handler error handling
- task cancellation cleanup

The public `Stream` Interface is useful, but the implementation lacks internal locality. Testing one rule requires rebuilding the fake websocket connection, fake context, message list, exception flow, and callbacks.

### Solution

Keep `Stream` as the public Module and deepen its implementation with internal Modules:

- A connection-session Module that performs one connected run: send queued requests, receive messages, parse `Response`, and hand off to dispatch.
- A reconnect loop Module that owns retry count, reconnect policy, lifecycle callback ordering, and sleep.
- A dispatch Module that owns `inline` / `task` / `queue`, handler errors, and task cleanup.

Avoid introducing public seams unless there are real adapters. Internal seams are enough if they make the implementation more testable without expanding the user-facing Interface.

### Benefits

- **Locality**: reconnect bugs live near reconnect rules; handler dispatch bugs live near dispatch rules.
- **Leverage**: tests can exercise lifecycle and dispatch behaviour through focused internal seams instead of reconstructing every `Stream` dependency.
- Public `Stream` usage remains stable for callers.

### Test surface

- Keep existing public `Stream` tests.
- Add focused dispatch tests for `inline`, `task`, and `queue` behaviour.
- Add focused reconnect lifecycle tests for retry count, permanent failure, and callback ordering.
- Run `just` and `just docs-build`.

## Candidate 3: Deepen WebSocket Response event interpretation

### Files

- `src/maicoin/ws/response.py`
- `src/maicoin/ws/*` payload models
- `tests/ws/test_response.py`
- `docs/websocket.md`

### Problem

`Response` preserves the MAX wire format with readable field names and alias parsing, but all event payloads share one model with many optional fields. Callers must know which optional payload field is meaningful for each event.

This makes event-to-payload rules shallow: `Response` parses data, but domain interpretation remains in caller knowledge or in ad hoc handler checks. Many response tests verify that parsing succeeds, but not that event payload invariants are concentrated.

### Solution

Keep raw `Response` as the wire-level Module, and add an event interpretation Module that centralizes rules such as:

- which payload fields are valid or required for each event;
- snapshot vs update payload expectations;
- private Order / account event payload expectations;
- M-Wallet event payload expectations.

Do not merge REST v3 and WebSocket raw payload models. This candidate stays within WebSocket raw transport semantics.

### Benefits

- **Locality**: WebSocket documentation drift updates one event interpretation Module.
- **Leverage**: handlers can ask a smaller Interface for the domain event rather than inspecting many optional fields.
- Tests move from “parse does not fail” toward event invariants and clearer error modes.

### Test surface

- Add table-driven tests for event-to-payload interpretation.
- Keep raw `Response` parsing tests for wire alias coverage.
- Add negative tests for missing required payloads where the interpretation Module promises validation.

## Candidate 4: Deepen REST v3 endpoint declaration

### Files

- `src/maicoin/v3/_endpoints/base.py`
- `src/maicoin/v3/_endpoints/*.py`
- `tests/v3/*`

### Problem

`EndpointSpec` and `EndpointExecutor` centralize request metadata and common response parsing, but each family method still has to choose:

- the `EndpointSpec`;
- the model type;
- `model`, `model_list`, `model_mapping`, or `raw`;
- params and path params.

For simple endpoints, the method body is still close to the endpoint declaration. The Module has improved depth, but parser metadata and parameter construction can still be more local.

### Solution

Deepen endpoint declarations so each declaration can include request metadata and response shape together:

- method/path/auth;
- response shape: raw, single model, list, mapping, or custom parser;
- path parameter names;
- parameter omission policy.

Family methods should mainly translate domain-facing arguments into declaration parameters and delegate execution.

### Benefits

- **Locality**: MAX REST v3 request/parse convention changes concentrate in endpoint declaration and executor logic.
- **Leverage**: one endpoint execution test surface can cover many endpoint methods.
- Endpoint tests can focus more on domain payloads and less on repeated request kwargs assertions.

### Test surface

- Extend `tests/v3/test_client.py` or add endpoint executor tests for declaration response shapes.
- Keep endpoint-family tests for public Client behaviour and representative request construction.

## Candidate 5: Deepen REST v3 test harness

### Files

- `tests/v3/conftest.py`
- `tests/v3/test_client.py`
- `tests/v3/test_public.py`
- `tests/v3/test_private.py`
- `tests/v3/test_funds.py`
- `tests/v3/test_convert.py`
- `tests/v3/test_m_wallet_private.py`

### Problem

Several REST v3 test files define similar fake HTTP helpers:

- `FakeResponse`
- `FakeSession`
- authenticated client builders
- `last_kwargs`
- auth payload decoders
- fixed nonce/base URL setup

The repeated helpers make request-construction knowledge spread across tests. Adding a new endpoint test requires rediscovering fake session shape and auth assertions.

### Solution

Create a deeper REST v3 test harness Module in `tests/v3/conftest.py` or `tests/v3/helpers.py`:

- reusable fake session/response adapters;
- fixtures for public and authenticated clients;
- request inspection helpers;
- auth payload decoding helpers.

Keep endpoint tests focused on domain payloads and expected public Client behaviour.

### Benefits

- **Locality**: test transport and auth assertion rules live in one Module.
- **Leverage**: every endpoint-family test can reuse the same fake transport and request-inspection Interface.
- Tests become shorter and easier to scan for domain behaviour.

### Test surface

- Refactor one endpoint family first to prove the harness is not hiding important assertions.
- Then migrate remaining endpoint tests in small batches.
- Run `just` after each batch.

## Candidate 6: Deepen destructive live-test safety

### Files

- `docs/plans/TODO.md`
- `docs/plans/archived/client-resilience-and-ergonomics-follow-ups.md`
- `tests/live/*`
- future destructive live-test files

### Problem

Read-only live tests exist, but destructive live tests remain intentionally deferred. If destructive tests are added directly, safety rules may scatter across tests:

- explicit environment gates;
- balance checks;
- market/currency allowlists;
- cleanup;
- manual recovery steps;
- dry-run or confirmation behaviour.

Those rules are not details of a single test. They are the Interface for the destructive live-test domain.

### Solution

Before adding destructive tests, design a destructive live-test safety Module. All destructive tests must cross that seam and should not implement their own gating or cleanup rules.

### Benefits

- **Locality**: safety rules are centralized and auditable.
- **Leverage**: new destructive tests describe the domain action while the safety Module handles gates and cleanup.
- Lower risk of accidental order placement, withdrawals, or CI execution.

### Test surface

- Unit-test safety gates without real credentials.
- Keep destructive tests opt-in and skipped by default.
- Document manual recovery steps before enabling any mutating live test.

## Candidate 7: Deepen public export and docs-reference maintenance

### Files

- `src/maicoin/v3/__init__.py`
- `src/maicoin/ws/__init__.py`
- `docs/site/content/reference/v3.md`
- `docs/site/content/reference/ws.md`
- `docs/site/mkdocs.yml`
- `tests/*`

### Problem

Public exports and MkDocs reference targets are maintained manually. A recent docs build failed because `maicoin.ws.ReconnectPolicy` was exported but not listed in `docs/site/content/reference/ws.md`, so `mkdocs_autorefs` could not resolve a cross-reference target.

This is a locality problem: the public export list and docs reference list encode related knowledge in separate places.

### Solution

Add a consistency check or generation pattern that verifies public exported names have docs reference targets when they are linked from docs.

Possible approaches:

- a test that checks selected exported names appear in reference docs;
- a small docs helper that generates reference pages from an explicit list;
- a policy that any newly exported public name must be added to reference docs, backed by a test.

### Benefits

- **Locality**: export/docs drift fails in one clear check.
- **Leverage**: new public exports get an immediate signal when docs targets are missing.
- `just docs-build` becomes less likely to fail from unrelated cross-reference drift.

### Test surface

- Add a focused docs consistency test or script.
- Keep `just docs-build` as the strict end-to-end gate.

## Recommended order

1. **REST v3 test harness** — small, low-risk, increases leverage for later REST v3 work.
2. **REST v3 model locality** — aligns with the completed endpoint-family split.
3. **WebSocket Stream lifecycle** — highest complexity reduction for WebSocket internals.
4. **Public export/docs-reference maintenance** — prevents recurring docs strict-mode failures.
5. **REST v3 endpoint declaration** — useful after the current endpoint family pattern has settled.
6. **WebSocket Response event interpretation** — valuable, but should be designed carefully to avoid over-constraining raw wire parsing.
7. **Destructive live-test safety** — do this immediately before any destructive live tests, not as speculative infrastructure.

## Non-goals

- Do not change public `Client` or `Stream` Interfaces without explicit compatibility planning.
- Do not merge REST v3 and WebSocket raw payload models.
- Do not replace Pydantic models with dataclasses without fresh benchmark evidence and a compatibility migration path.
- Do not add hypothetical seams with only one adapter unless they are internal seams that clearly improve locality and tests.
