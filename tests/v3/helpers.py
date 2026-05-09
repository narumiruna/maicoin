from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import cast

from maicoin.v3 import Client

BASE_URL = "https://example.test"
FIXED_NONCE = 123456
API_KEY = "key"
API_SECRET = "secret"


class FakeResponse:
    def __init__(self, payload: object, *, status_code: int = 200, headers: Mapping[str, str] | None = None) -> None:
        self.payload = payload
        self.status_code = status_code
        self.headers = dict(headers or {})
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, response: object) -> None:
        if isinstance(response, FakeResponse):
            self.responses: list[FakeResponse] = [response]
        elif isinstance(response, list) and all(isinstance(item, FakeResponse) for item in response):
            self.responses = cast("list[FakeResponse]", response)
        else:
            self.responses = [FakeResponse(response)]
        self.calls: list[dict[str, object]] = []
        self.closed = False

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if len(self.responses) == 1:
            return self.responses[0]
        return self.responses.pop(0)

    async def aclose(self) -> None:
        self.closed = True


class PagedFakeSession:
    def __init__(self, pages: list[object]) -> None:
        self.pages = pages
        self.calls: list[dict[str, object]] = []
        self.closed = False

    async def request(self, method: str, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        page = self.pages[len(self.calls) - 1]
        return FakeResponse(page)

    async def aclose(self) -> None:
        self.closed = True


def public_client(session: FakeSession | PagedFakeSession) -> Client:
    return Client(base_url=BASE_URL, session=session)


def authenticated_client(session: FakeSession | PagedFakeSession) -> Client:
    return Client(
        api_key=API_KEY,
        api_secret=API_SECRET,
        base_url=BASE_URL,
        session=session,
        nonce_factory=lambda: FIXED_NONCE,
    )


def last_call(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[-1])


def call_kwargs(session: FakeSession | PagedFakeSession, index: int = -1) -> Mapping[str, object]:
    return cast("Mapping[str, object]", session.calls[index]["kwargs"])


def last_kwargs(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return call_kwargs(session)


def last_params(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", last_kwargs(session)["params"])


def last_json(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return cast("Mapping[str, object]", last_kwargs(session)["json"])


def request_headers(session: FakeSession | PagedFakeSession, index: int = -1) -> Mapping[str, str]:
    return cast("Mapping[str, str]", call_kwargs(session, index)["headers"])


def auth_payload(session: FakeSession | PagedFakeSession, index: int = -1) -> Mapping[str, object]:
    headers = request_headers(session, index)
    payload = base64.b64decode(headers["X-MAX-PAYLOAD"]).decode()
    return cast("Mapping[str, object]", json.loads(payload))


def last_payload(session: FakeSession | PagedFakeSession) -> Mapping[str, object]:
    return auth_payload(session)
