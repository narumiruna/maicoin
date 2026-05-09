# TODO

## Active Follow-Ups

Follow-up plans:

- [`plans/client-resilience-and-ergonomics-follow-ups.md`](plans/client-resilience-and-ergonomics-follow-ups.md)
- [`plans/codebase-architecture-deepening-opportunities.md`](plans/codebase-architecture-deepening-opportunities.md)

### Architecture Deepening

Plan: [`plans/codebase-architecture-deepening-opportunities.md`](plans/codebase-architecture-deepening-opportunities.md)

- [ ] Deepen the REST v3 test harness so fake transport, authenticated clients, request inspection, and auth payload decoding live behind one test Module.
- [ ] Split REST v3 raw models by domain family while preserving public `maicoin.v3` and `maicoin.v3.models` imports.
- [ ] Deepen the WebSocket Stream lifecycle implementation so reconnect/session and response dispatch rules have stronger locality.
- [ ] Add a public export / docs-reference consistency check to prevent strict MkDocs autorefs drift.
- [ ] Consider deeper REST v3 endpoint declarations that combine request metadata with response shape once the current endpoint-family pattern settles.
- [ ] Explore WebSocket Response event interpretation only after deciding the intended Interface for event-to-payload invariants.

### Release / Package Polish

- [ ] Fill in package metadata gaps, including the empty `description` in `pyproject.toml`.
- [ ] Verify README, MkDocs docs, examples, and PyPI-facing metadata are consistent before the next release.
- [ ] Run the local release-readiness gates, including `just` and `just docs-build`.

### Official API Drift Audit

- [ ] Compare REST v3 client coverage, payload fields, and naming against the official MAX HTTP API v3 documentation.
- [ ] Compare WebSocket channels, subscription payloads, response fields, and auth behavior against the official WebSocket documentation.
- [ ] Record and prioritize any missing, changed, or deprecated API behavior before adding new features.

### Documentation / Examples Polish

- [ ] Add practical examples for retry behavior, pagination helpers, and async client lifecycle management.
- [ ] Add richer WebSocket examples covering reconnect behavior, handler dispatch, and private stream setup.
- [ ] Clarify safety guidance for private state-changing methods with explicit warnings and safe usage patterns.

### Destructive Live Tests

Plan archived: [`archived/live-integration-tests-plan.md`](archived/live-integration-tests-plan.md). Read-only public and private live tests are implemented; destructive live tests remain intentionally out of scope until a separate safety design pass.

- [ ] Design opt-in destructive live tests with explicit environment gates, balance checks, cleanup, and manual recovery steps.

### Dataclass Low-Level Model Experiment

Plan archived: [`archived/dataclass-low-level-models-plan.md`](archived/dataclass-low-level-models-plan.md).

- [ ] Revisit low-level dataclass models only if fresh benchmark evidence shows value and there is a compatibility migration path.
