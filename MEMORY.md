# MEMORY.md

## GOTCHA

- REST v3 `Client` now delegates endpoint families to internal `src/maicoin/v3/_endpoints/` modules. Add or update `EndpointSpec` constants and `EndpointExecutor` calls in the relevant family module, while keeping public `Client` method signatures stable as thin delegators.
- If REST v3 raw models are needed, add them to the matching `src/maicoin/v3/models/<domain>.py` module and re-export public names from `src/maicoin/v3/models/__init__.py` and `src/maicoin/v3/__init__.py` as needed.
- REST v3 endpoint tests should use `tests.v3.helpers` (`FakeResponse`, `FakeSession`, `PagedFakeSession`, `public_client`, `authenticated_client`) and inspect requests with helpers like `last_kwargs`, `last_params`, `last_json`, `request_headers`, `auth_payload`, and `last_payload`.
- WebSocket `Stream` lifecycle internals are split under `src/maicoin/ws/_stream/`; dispatch mode, handler error, and task cleanup changes belong in `src/maicoin/ws/_stream/dispatch.py`.

## TASTE
