# Architecture deepening follow-up plan

## Goal

Deepen five current architecture opportunities found in the May 2026 review without reopening archived decisions that still lack new evidence. Success means each chosen slice improves locality or leverage at an existing seam, preserves public behavior unless explicitly documented, and has tests that exercise the same interface callers use.

## Context

The first architecture pass is already complete: REST v3 endpoint families, REST raw model locality, WebSocket Stream lifecycle internals, REST test helpers, and docs reference checks were previously implemented or archived. This plan is for follow-up work only.

No project `CONTEXT.md` or `docs/adr/` exists at the time of writing. Use the current codebase vocabulary: REST v3, Order, funds, Convert, M-Wallet, WebSocket Stream, Subscription, Response, and live tests.

## Architecture

Each slice should keep the public `maicoin.v3.Client` and `maicoin.ws.Stream` interfaces stable unless the specific slice is explicitly about public validation. Prefer internal modules when one adapter would be hypothetical, and use public model validation only when the rule is already part of the caller-facing interface.

## Non-Goals

- Do not deepen REST `EndpointSpec` into response-shape declarations in this plan; `docs/plans/archived/todo-follow-up-decisions.md` says to revisit only with new route-audit, docs-generation, or repeated-boilerplate pressure.
- Do not add a WebSocket Response event interpretation module in this plan; the archived decision keeps `Response` as the wire-level model until normalized event callers exist.
- Do not add destructive live tests in this plan; the safety design exists, but there are no destructive test adapters yet.
- Do not centralize test payload builders just because they repeat; keep domain sample payloads near the tests that explain them.

## Assumptions

- Public import compatibility is more important than making internal modules visually small.
- Validation that rejects previously remote-only errors is acceptable only when the official MAX docs make the invariant unambiguous or existing tests already rely on it.
- Live WebSocket smoke tests must stay behind the existing `live` marker and `RUN_LIVE_TESTS=1` gate.

## Unknowns

- The exact REST invariant rules for lookup and create methods must be confirmed against the official MAX HTTP v3 docs before adding local validation.
- The exact Subscription channel requirements must be confirmed against the official MAX WebSocket docs before making validation strict.
- The WebSocket public live smoke timeout and subscribed channel should be chosen from a stable public channel after a quick local/manual trial.

## Plan

### Slice 1: REST request invariant module

- [ ] Audit `order_id/client_oid`, `txid/uuid`, `from_amount/to_amount`, and similar REST v3 argument pairs in `src/maicoin/v3/_endpoints/`; verify the intended rule with the official HTTP v3 docs and record the list in the implementation PR description or plan update.
- [ ] Add a small internal invariant module under `src/maicoin/v3/_endpoints/` to express `at_least_one` and `exactly_one` request argument rules; verify with focused unit tests for valid, missing, and ambiguous inputs.
- [ ] Apply the invariant module to lookup and create methods in `order_intake_history.py`, `funds.py`, and `convert.py` without changing successful request payloads; verify with `uv run pytest -v -s tests/v3`.
- [ ] Update REST docs only if a public error mode changes from remote MAX error to local `ValueError`; verify with `just docs-build` if docs changed.

### Slice 2: WebSocket Subscription channel intent

- [ ] Audit channel-specific Subscription rules for `book`, `trade`, `ticker`, `kline`, `market_status`, `pool_quota`, and `user`; verify each rule against the official WebSocket docs and current tests in `tests/ws/test_subscription.py`.
- [ ] Add Subscription validation or constructor helpers that keep valid current examples working while rejecting unambiguous invalid channel/field combinations; verify with positive and negative tests in `tests/ws/test_subscription.py`.
- [ ] Update `docs/site/content/websocket.md` and examples only if the public construction pattern changes; verify with `just docs-build` and `uv run pytest -v -s tests/ws/test_subscription.py tests/ws/test_request.py`.

### Slice 3: WebSocket queued request and replay module

- [ ] Design an internal queued-request module under `src/maicoin/ws/_stream/` that owns auth-first ordering, subscription appends, public mutation behavior, and replay order; verify the intended public behavior against existing `Stream.requests`, `auth()`, and `subscribe()` tests before editing.
- [ ] Move request queue and replay preparation from `Stream` / `ConnectedSession` into the new module while preserving `Stream.requests` compatibility if it is still public; verify with `uv run pytest -v -s tests/ws/test_stream.py tests/ws/test_stream_session.py`.
- [ ] Remove or simplify obsolete Stream pass-through internals only when no tests or docs depend on them; verify with `rg '_should_reconnect|_dispatch|_call_handler|_call_lifecycle|_cancel_handler_tasks|_handler_tasks' src tests`.
- [ ] Run the full WebSocket test set after the slice; verify with `uv run pytest -v -s tests/ws`.

### Slice 4: Public export and docs-reference manifest

- [ ] Define a docs-reference manifest in `tests/test_docs_reference.py` that states which `maicoin.v3` and `maicoin.ws` exports require top-level reference targets and which are covered by grouped targets such as `maicoin.v3.models`; verify the manifest covers current `__all__` names.
- [ ] Extend the reference tests to apply the manifest to both v3 and WebSocket exports; verify with `uv run pytest -v -s tests/test_docs_reference.py`.
- [ ] Update `docs/site/content/reference/v3.md` or `docs/site/content/reference/ws.md` only for genuinely missing references exposed by the manifest; verify with `just docs-build`.

### Slice 5: WebSocket public live smoke module

- [ ] Add a `tests/live/test_websocket_public_live.py` smoke test that subscribes to one stable public WebSocket channel, waits for a bounded first `Response`, and closes/cancels cleanly; verify it is skipped by default with `uv run pytest -v -s tests/live/test_websocket_public_live.py`.
- [ ] Reuse existing live gating from `tests/live/conftest.py` and do not require credentials for the public WebSocket smoke; verify with collection output that `RUN_LIVE_TESTS` controls execution.
- [ ] Add timeout, channel, and market configuration through environment variables only where needed for reliable local execution; verify by documenting the variables in `docs/site/content/live-tests.md`.
- [ ] Run the public live smoke manually when network and MAX availability are acceptable; verify with `RUN_LIVE_TESTS=1 uv run pytest -v -s tests/live/test_websocket_public_live.py` and record the result in the plan or PR.

## Risks

- Local REST validation can become stricter than MAX if docs are ambiguous or stale; mitigate by validating only unambiguous invariants and preserving remote behavior otherwise.
- Subscription validation can break users who rely on permissive model construction; mitigate by limiting strict rules to documented invalid combinations or by adding named constructors first.
- WebSocket live tests can be flaky because they depend on network and exchange availability; mitigate with short bounded timeouts, default skip behavior, and a single public channel.
- A docs-reference manifest can become another shallow policy layer if it duplicates mkdocstrings behavior without explaining coverage rules; mitigate by keeping the manifest small and explicit.

## Rollback / Recovery

- Revert a slice by reverting only its implementation and tests; the slices are intended to be independent.
- If stricter public validation causes compatibility concern, keep the tests but mark the validation task incomplete and convert the rule into documentation or helper constructors instead of hard rejection.
- If WebSocket live smoke is flaky, keep the test skipped by default and either tune timeout/channel settings or remove the live slice without affecting unit tests.

## Completion Checklist

- [ ] REST request invariants are implemented or explicitly marked not applicable, and verified by `uv run pytest -v -s tests/v3`.
- [ ] WebSocket Subscription intent is implemented or explicitly marked not applicable, and verified by `uv run pytest -v -s tests/ws/test_subscription.py tests/ws/test_request.py`.
- [ ] WebSocket queued request/replay locality is implemented or explicitly marked not applicable, and verified by `uv run pytest -v -s tests/ws`.
- [ ] Public export/docs-reference policy covers both v3 and WebSocket exports, and is verified by `uv run pytest -v -s tests/test_docs_reference.py` plus `just docs-build` when reference docs change.
- [ ] WebSocket public live smoke is added or explicitly marked not applicable, is skipped by default, and has a recorded `RUN_LIVE_TESTS=1` result when live network verification is available.
- [ ] The full local gate passes after all selected slices, verified by `just`.
