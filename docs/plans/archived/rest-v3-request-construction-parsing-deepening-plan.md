# REST v3 Request Construction and Parsing Deepening Plan

Status: **implemented and archived**.

## Goal

Deepen the REST v3 request-construction and response-parsing module so endpoint methods get more behavior behind a smaller internal interface. Keep the public `maicoin.v3.Client` interface stable.

This should improve **locality** for MAX HTTP v3 conventions and increase **leverage** when adding or auditing endpoints.

## Current Friction

`src/maicoin/v3/client.py` repeats the same endpoint implementation pattern across many methods:

- choose HTTP method and path
- compact optional params
- decide whether auth is required
- rely on `Client.request(...)` for GET query vs POST/DELETE JSON placement
- parse response payload with `Model.model_validate(...)` or list/dict comprehensions

The useful transport behavior already lives in `Client.request(...)`, but endpoint methods still need to manually know too many request and parsing conventions. Tests also repeat fake-session plumbing and request-kwargs assertions across `tests/v3/*`.

## Implemented Scope

This plan was implemented by adding internal endpoint execution helpers to `src/maicoin/v3/client.py`:

- `_request_model(...)`
- `_request_model_list(...)`
- `_request_model_mapping(...)`

Most typed REST v3 endpoint methods now delegate request execution and Pydantic response parsing to these helpers while preserving public `Client` method names, signatures, return types, and sync wrappers. Custom/raw payload shapes such as K-line row parsing and raw M-Wallet limit/index-price dictionaries remain explicit at the endpoint method.

The helper seam is covered in `tests/v3/test_client.py`, and the existing endpoint behavior tests continue to verify public behavior.

## Proposed Direction

Introduce a deeper internal REST v3 endpoint execution module while preserving current public methods.

Possible shape:

- Keep `Client.request(...)` as the low-level escape hatch.
- Add internal helpers for common endpoint shapes, for example:
  - authenticated vs public endpoint calls
  - optional-param compaction
  - list payload parsing
  - single-model payload parsing
  - mapping payload parsing
  - custom row parsing for shapes like K-line arrays
- Move repeated endpoint rules behind this internal seam gradually.
- Avoid introducing a broad adapter seam unless there are at least two real adapters.

Do **not** merge REST v3 and WebSocket raw payload models. Existing project decision is to keep transport-specific raw models separate and use normalized domain models only if there is real cross-transport need.

## Scope

### In Scope

- Internal REST v3 request construction and parsing helpers.
- Refactor a representative endpoint family first, likely public market-data methods, then authenticated Order/funds methods if the shape holds.
- Preserve existing `Client` method names, signatures, return types, and sync wrappers.
- Improve v3 test fixtures where it directly supports the refactor.

### Out of Scope

- Splitting all of `Client` into endpoint-family modules in the first pass.
- Changing public imports from `maicoin.v3`.
- Changing raw Pydantic models or merging them with WebSocket models.
- Destructive live tests.

## Candidate Implementation Steps

1. Inventory endpoint shapes in `src/maicoin/v3/client.py`:
   - single model
   - list of models
   - dict of models
   - raw dict
   - custom array-row parser
   - no-body / empty response handling
2. Design a small internal helper interface and apply the deletion test.
3. Add focused unit tests for the helper interface.
4. Refactor low-risk public endpoints first:
   - `markets`
   - `currencies`
   - `timestamp`
   - `trades`
   - `tickers`
   - `ticker`
5. Refactor one authenticated read family, likely Order history/lookups.
6. Decide whether funds, Convert, and M-Wallet should follow immediately or wait for a second pass.
7. Consolidate duplicated v3 fake HTTP test helpers into `tests/v3/conftest.py` if doing so reduces noise without hiding endpoint-specific assertions.
8. Run local gates.

## Test Plan

Run at minimum:

```shell
just test
just type
just lint
```

For broader confidence before merging:

```shell
just
```

Focus tests on the new internal helper interface plus unchanged public `Client` behavior.

## Open Questions

- What is the smallest helper interface that improves **depth** without becoming a mini framework?
- Should endpoint metadata be explicit data objects, or should helpers stay as typed functions called by endpoint methods?
- How much v3 test fixture consolidation is worth doing in the same change?
- Should sync wrappers remain untouched in this pass except where tests prove behavior is preserved?
