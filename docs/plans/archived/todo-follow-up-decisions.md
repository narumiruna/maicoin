# TODO follow-up decisions

Date: 2026-05-15 (Asia/Taipei)

This records the architecture and model experiments that were intentionally left as TODO items after earlier deepening work.

## REST endpoint declarations

Decision: do not deepen endpoint declarations now.

The current split is readable: endpoint families own domain methods, `EndpointSpec` owns route/auth metadata, and tests use shared helpers for request inspection. Combining route metadata with response shape would add another abstraction without removing a current pain point.

Revisit only when one of these conditions is true:

- A new endpoint family repeats enough parse/wrap boilerplate that the pattern is error-prone.
- A route audit needs machine-readable response-shape metadata.
- Public docs generation needs endpoint declarations as structured input.

## WebSocket event interpretation

Decision: keep `Response` as the wire-level public model and avoid a second interpretation layer for now.

The response model already exposes typed optional payload fields for documented events. A stricter event-to-payload invariant layer would be useful only if downstream code needs dispatch on normalized payload kinds instead of raw MAX events.

If that need appears, add an internal interpretation module first. It should map `Event` to a small descriptor containing the expected payload field, snapshot/update kind, and whether the event is public, spot private, or M-Wallet private. Do not make that module public until it has real caller pressure.

## Dataclass low-level model experiment

Decision: keep Pydantic models.

There is no fresh benchmark evidence showing that dataclass-based low-level models would improve this package enough to justify a migration. Pydantic also remains useful for alias handling, validation, and docs reference generation.

Revisit only with:

- A benchmark that covers parsing realistic REST and WebSocket payloads.
- A compatibility plan for public model imports and attributes.
- A clear migration path for generated docs and tests.
