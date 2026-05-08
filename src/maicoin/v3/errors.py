from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol
from typing import cast


class Response(Protocol):
    content: bytes
    status_code: int
    text: str

    def json(self) -> object: ...


class MaxAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, payload: object = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class MaxHTTPError(MaxAPIError):
    pass


def raise_for_response_status(response: Response) -> None:
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
    if not isinstance(payload, Mapping):
        return

    payload_mapping = cast("Mapping[object, object]", payload)
    if "error" not in payload_mapping:
        return

    raise MaxAPIError(str(payload_mapping["error"]), payload=payload)
