"""Error types and response-validation helpers for the REST v3 client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol
from typing import cast


class Response(Protocol):
    """Minimal HTTP response protocol used by the error helpers.

    Compatible with `httpx.Response` and most session libraries.
    """

    content: bytes
    status_code: int
    text: str

    def json(self) -> object: ...


class MaxAPIError(Exception):
    """Raised when MAX returns a structured `{"error": ...}` payload.

    Attributes:
        status_code: HTTP status code, when known.
        payload: Raw response body that triggered the error, useful for
            inspecting MAX's `error.code` / `error.message` fields.
    """

    def __init__(self, message: str, *, status_code: int | None = None, payload: object = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class MaxHTTPError(MaxAPIError):
    """Raised for non-2xx HTTP responses without a recognized MAX error body.

    Behaves like [`MaxAPIError`][maicoin.v3.MaxAPIError] — catch it as a
    subclass when you want to distinguish HTTP-level failures (network,
    rate-limit, gateway) from API-level failures.
    """


def raise_for_response_status(response: Response) -> None:
    """Raise [`MaxHTTPError`][maicoin.v3.MaxHTTPError] if `response` has a 4xx/5xx status.

    The error message is taken from `payload["error"]`, `payload["message"]`,
    the raw body, or `response.text`, in that order.
    """
    status_code = response.status_code
    if status_code < 400:
        return

    payload: object
    try:
        payload = response.json()
    except ValueError:
        payload = getattr(response, "text", "")

    if isinstance(payload, Mapping):
        payload_mapping = cast("Mapping[object, object]", payload)
        message = str(payload_mapping.get("error") or payload_mapping.get("message") or payload)
    else:
        message = str(payload)

    raise MaxHTTPError(message, status_code=status_code, payload=payload)


def raise_for_api_error(payload: object) -> None:
    """Raise [`MaxAPIError`][maicoin.v3.MaxAPIError] if `payload` carries an `error` key.

    MAX occasionally returns 200 OK with an error body for endpoints like
    convert and order placement. Call this after parsing the JSON body.
    """
    if not isinstance(payload, Mapping):
        return

    payload_mapping = cast("Mapping[object, object]", payload)
    if "error" not in payload_mapping:
        return

    raise MaxAPIError(str(payload_mapping["error"]), payload=payload)
