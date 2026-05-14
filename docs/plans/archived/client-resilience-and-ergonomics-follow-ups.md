# Client Resilience and Ergonomics Follow-Up Plan

Status: **archived; deferred follow-ups are tracked in TODO**.

The implemented client resilience and ergonomics work has been archived at [`completed-client-resilience-and-ergonomics-plan.md`](completed-client-resilience-and-ergonomics-plan.md).

There is no remaining core client-resilience implementation work in this plan. The only related follow-ups are intentionally deferred safety/benchmark tasks.

## Remaining Follow-Ups

### Destructive Live Tests

Plan reference: [`live-integration-tests-plan.md`](live-integration-tests-plan.md)

Deferred TODO: design opt-in destructive live tests with explicit environment gates, balance checks, cleanup, and manual recovery steps.

Notes:

- Read-only live tests already exist.
- Mutating tests that place/cancel orders or otherwise change account state require a separate safety design.
- Future destructive tests must not run in normal CI.

### Dataclass Low-Level Models

Plan reference: [`dataclass-low-level-models-plan.md`](dataclass-low-level-models-plan.md)

Deferred TODO: revisit low-level dataclass models only if fresh benchmark evidence shows value and there is a compatibility migration path.

Notes:

- The previous benchmark showed Pydantic v2 was faster than the tested manual dataclass parser.
- Do not replace Pydantic models without new benchmark evidence.
