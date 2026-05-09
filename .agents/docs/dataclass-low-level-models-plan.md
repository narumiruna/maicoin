# Low-Level Dataclass Models Plan

## Goal

Introduce fast, low-overhead dataclass response/request types for lower-level users while keeping Pydantic models available for higher-level validation, error messages, and backwards-compatible APIs.

This is not a plan to remove Pydantic. Instead, the package should support three related layers:

- **Transport data layer**: `@dataclass(slots=True, frozen=True)` types with minimal conversion and fast parsing. These stay close to REST v3 or WebSocket payload shape.
- **Transport validated layer**: existing Pydantic models for backwards-compatible, transport-specific validation.
- **Unified high-level layer**: Pydantic `BaseModel` domain models that can represent equivalent results from both REST v3 and WebSocket sources.

## Non-Goals

- Do not remove Pydantic as a dependency in the first pass.
- Do not break existing imports such as `from maicoin.ws import Response` or `from maicoin.v3 import Ticker`.
- Do not change default `Client` or `Stream` return types until the dataclass layer is stable.
- Do not add destructive live API tests as part of this work.

## Proposed Public API

Keep existing Pydantic names as the high-level API:

```python
from maicoin.ws import Response
from maicoin.v3 import Ticker
```

Add dataclass types under explicit data namespaces:

```python
from maicoin.ws.data import ResponseData
from maicoin.v3.data import TickerData
```

Later, add opt-in return modes:

```python
client = Client(model="pydantic")  # default, existing behavior
client = Client(model="data")      # returns dataclasses
client = Client(model="raw")       # returns dict/list payloads

stream = Stream(model="pydantic")  # default, existing behavior
stream = Stream(model="data")      # handlers receive dataclasses
```

Pydantic models should support validating dataclass instances where useful:

```python
pydantic_response = Response.model_validate(response_data)
```

This requires Pydantic models to use `from_attributes=True` or equivalent configuration.

Add a separate unified high-level API for users who do not want to care whether data came from REST v3 or WebSocket:

```python
from maicoin.models import Ticker
from maicoin.models import Trade

rest_ticker = Ticker.from_v3(v3_ticker_data)
ws_ticker = Ticker.from_ws(ws_ticker_data)
```

The exact namespace can change, but the important distinction is:

- `maicoin.v3.data.TickerData`: fast REST v3 payload-shaped dataclass.
- `maicoin.ws.data.TickerData`: fast WebSocket payload-shaped dataclass.
- `maicoin.models.Ticker`: normalized Pydantic domain model that accepts either source.

## Model Layer Responsibilities

### Dataclass Data Layer

Responsibilities:

- Represent trusted API payloads with typed attributes.
- Perform only necessary parsing:
  - alias mapping, for example `M` -> `market`;
  - nested object construction;
  - timestamp conversion where the public attribute is `datetime`;
  - enum construction where the current public type is an enum.
- Serialize outbound WebSocket requests quickly with `orjson`.

Recommended shape:

```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class TickerData:
    market: str
    open: str
    high: str
    low: str
    close: str
    volume: str
    volume_in_btc: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "TickerData": ...
```

### Transport Pydantic Validated Layer

Responsibilities:

- Preserve current transport-specific model names and behavior.
- Provide validation and helpful user-facing errors for REST v3 and WebSocket payloads.
- Support construction from raw mappings and dataclass instances.
- Remain the default API until a future major-version decision says otherwise.

### Unified High-Level Pydantic Layer

Responsibilities:

- Provide source-agnostic domain models for equivalent REST v3 and WebSocket concepts.
- Normalize naming and types across transports.
- Preserve enough source metadata for users to debug where a value came from.
- Avoid replacing low-level dataclasses; instead, consume them.

Candidate namespace:

- `src/maicoin/models.py` for common domain models, or
- `src/maicoin/unified/` if the API grows beyond a few models.

Candidate unified models:

- `Ticker`
- `Trade`
- `Order`
- `Balance`
- `KLine`
- `MarketStatus`

Example shape:

```python
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict


class Source(StrEnum):
    REST_V3 = "rest_v3"
    WEBSOCKET = "websocket"


class Ticker(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source: Source
    market: str
    open: str | None = None
    high: str | None = None
    low: str | None = None
    close: str | None = None
    last: str | None = None
    volume: str | None = None
    volume_in_btc: str | None = None
    observed_at: datetime | int | None = None

    @classmethod
    def from_v3(cls, ticker: object) -> "Ticker": ...

    @classmethod
    def from_ws(cls, ticker: object) -> "Ticker": ...
```

Normalization should be explicit. If REST v3 and WebSocket expose different semantics, keep fields optional or use separate names instead of pretending they are identical.

## Best First Target: WebSocket Responses

WebSocket responses are the best first target because they are stream-oriented and may be parsed many times per connection.

Candidate modules:

- `src/maicoin/ws/response.py`
- `src/maicoin/ws/ticker.py`
- `src/maicoin/ws/trade.py`
- `src/maicoin/ws/order.py`
- `src/maicoin/ws/balance.py`
- `src/maicoin/ws/kline.py`
- `src/maicoin/ws/m_wallet.py`
- `src/maicoin/ws/market_status.py`

Key parser entry points:

```python
ResponseData.from_json(data: str | bytes) -> ResponseData
ResponseData.from_mapping(payload: Mapping[str, object]) -> ResponseData
```

`Stream` can later choose between:

```python
Response.model_validate_json(data)  # current default
ResponseData.from_json(data)        # opt-in fast path
```

## Second Target: WebSocket Requests

`src/maicoin/ws/request.py` is a good dataclass target because it mostly serializes outbound messages.

Required behavior to preserve:

- `api_key` must serialize as `apiKey`.
- `None` fields must be omitted.
- unsubscribe must continue to use the documented singular `subscription` key.
- `Request.message()` must return a JSON string compatible with the existing tests and MAX WebSocket API.

Possible implementation:

```python
@dataclass(slots=True, frozen=True)
class RequestData:
    ...

    def message(self) -> str:
        return orjson.dumps(self.to_payload()).decode()
```

Existing `Request` can remain Pydantic or become a thin high-level wrapper later.

## Third Target: REST v3 Response Models

REST v3 models are lower throughput than WebSocket responses, but many are simple data containers and are good candidates once the WebSocket data-layer pattern is proven.

Candidate module:

- `src/maicoin/v3/data.py` or `src/maicoin/v3/data/`

Most models in `src/maicoin/v3/models.py` can have direct dataclass equivalents.

Special cases requiring alias handling:

- `InternalTransfer.from_` maps from JSON key `from`.
- `FundTransactionDeposit.from_` maps from JSON key `from`.
- `FundTransactionTransfer.from_` maps from JSON key `from`.

Client mode can then choose among:

```python
raw_payload = client.request(...)
TickerData.from_mapping(raw_payload)
Ticker.model_validate(raw_payload)
```

## Unified API Strategy

The unified high-level layer should be built after both transport data layers exist, because it should adapt from low-level dataclasses rather than parse raw payloads directly.

Recommended conversion direction:

```text
raw payload -> transport dataclass -> unified Pydantic model
raw payload -> transport Pydantic model  # existing compatibility path
```

Avoid making the unified model depend on one transport's field names. For example, REST v3 ticker uses fields like `buy`, `sell`, `last`, and `vol`, while WebSocket ticker uses compact aliases and `close`. A unified `Ticker` should name the domain concept clearly and document fields that are unavailable from one source.

Potential opt-in APIs after the data layer is stable:

```python
client = Client(model="unified")
stream = Stream(model="unified")
```

or explicit adapters:

```python
from maicoin.models import Ticker

Ticker.from_v3(v3_ticker_data)
Ticker.from_ws(ws_response_data.ticker)
```

Prefer explicit adapters first. Add `model="unified"` only after the normalized domain model shape is proven.

## Parsing Helper Strategy

Avoid a large generic validation framework. Prefer small helpers that make alias mapping explicit and cheap.

Potential helper module:

- `src/maicoin/_data.py`

Candidate helpers:

```python
def require_mapping(value: object) -> Mapping[str, object]: ...
def optional_str(payload: Mapping[str, object], key: str) -> str | None: ...
def parse_ms_datetime(value: object | None) -> datetime | None: ...
def parse_list(value: object, parser: Callable[[Mapping[str, object]], T]) -> list[T]: ...
```

Keep helpers narrow. If the helper layer starts becoming a validation framework, prefer direct per-model `from_mapping()` methods instead.

## Compatibility Plan

Phase 1 should add dataclass APIs without changing existing behavior.

Compatibility rules:

- Existing Pydantic models keep their current names.
- Existing tests using `model_validate()` continue to pass.
- New dataclass tests should assert equality, aliases, timestamp conversion, enum conversion, and nested parsing.
- `Stream()` and `Client()` default behavior remains unchanged.

## Implementation Phases

### Phase 1: Add WebSocket Dataclass Response Layer

- Add `maicoin.ws.data` dataclasses for response-related payloads.
- Add `ResponseData.from_json()` and `ResponseData.from_mapping()`.
- Add tests mirroring key `tests/ws/test_response.py` cases for the dataclass parser.
- Do not change `Stream` default behavior.

### Phase 2: Add Opt-In WebSocket Stream Mode

- Add `Stream(model="pydantic" | "data")`.
- Keep `"pydantic"` as the default.
- Parse with `ResponseData.from_json()` when `model="data"`.
- Add tests for handler payload type.

### Phase 3: Add WebSocket Request Dataclasses

- Add dataclass request serialization.
- Keep `apiKey` alias and `exclude_none` behavior.
- Either expose it as `RequestData` or use it internally behind existing `Request.message()`.

### Phase 4: Add REST v3 Dataclass Models

- Add `maicoin.v3.data` dataclasses.
- Implement explicit `from_mapping()` constructors.
- Add tests for nested models and `from` alias fields.

### Phase 5: Add Opt-In REST Client Mode

- Add `Client(model="pydantic" | "data" | "raw")`.
- Keep `"pydantic"` as the default.
- Ensure all current high-level methods still return existing Pydantic models by default.

### Phase 6: Add Unified High-Level Pydantic Models

- Add source-agnostic Pydantic domain models under `maicoin.models` or `maicoin.unified`.
- Add explicit adapters such as `Ticker.from_v3(...)` and `Ticker.from_ws(...)`.
- Start with shared concepts that exist in both REST v3 and WebSocket, especially ticker, trade, order, balance, and kline.
- Keep source metadata on unified models.
- Do not add `Client(model="unified")` or `Stream(model="unified")` until explicit adapters are tested and stable.

### Phase 7: Add Optional Unified Return Mode

- Add `Client(model="unified")` for endpoints that have a clear unified domain model.
- Add `Stream(model="unified")` for WebSocket events that have a clear unified domain model.
- For source-specific events without a unified model, either return transport-specific dataclasses or raise a clear unsupported-mode error.

## Verification

For every phase, run:

```shell
just
```

For WebSocket parsing changes, include focused tests for:

- response event aliases;
- nested orders/trades/balances/tickers;
- millisecond timestamp conversion;
- M-Wallet response payloads;
- unsubscribe request serialization.

For REST v3 parsing changes, include focused tests for:

- nested currency networks;
- order enum fields;
- `from` -> `from_` alias mapping;
- M-Wallet liquidation detail nesting.

For unified high-level models, include focused tests for:

- constructing the same unified model from REST v3 dataclass input and WebSocket dataclass input;
- source metadata preservation;
- explicit handling of fields that exist in only one transport;
- Pydantic validation from dataclass instances via `from_attributes=True` where applicable.

## Open Questions

- Should dataclass types be exported from package-level `__init__.py`, or only from `maicoin.ws.data` and `maicoin.v3.data`?
- Should dataclass response fields use `datetime` exactly like current WebSocket Pydantic models, or keep raw integer timestamps for maximum speed?
- Should invalid enum values raise immediately in dataclass parsing, or be stored as raw strings for speed and forward compatibility?
- Should `Client(model="data")` be typed with overloads for better static typing?
- Should unified domain models live in `maicoin.models` or `maicoin.unified`?
- Should unified `Ticker` expose both `close` and `last`, or normalize to one canonical field with documented source-specific aliases?
- Should `Client(model="unified")` return unified models only for endpoints with clear cross-transport equivalents, or should every method have a unified wrapper type?
