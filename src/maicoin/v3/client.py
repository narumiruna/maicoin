from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from typing import Protocol
from urllib.parse import urljoin

import requests

from .auth import build_auth_headers
from .auth import generate_nonce
from .errors import Response
from .errors import raise_for_api_error
from .errors import raise_for_response_status

BASE_URL = "https://max-api.maicoin.com"
DEFAULT_TIMEOUT = 10


class RequestSession(Protocol):
    def request(self, method: str, url: str, **kwargs: object) -> Response: ...


class Client:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        *,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: RequestSession | None = None,
        nonce_factory: Callable[[], int] = generate_nonce,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session() if session is None else session
        self.nonce_factory = nonce_factory

    def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, object] | None = None,
        *,
        auth: bool = False,
    ) -> object:
        normalized_method = method.upper()
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = urljoin(self.base_url, normalized_path)
        request_params = dict(params or {})
        headers: dict[str, str] = {}

        if auth:
            if self.api_key is None or self.api_secret is None:
                msg = "api_key and api_secret are required for authenticated requests"
                raise ValueError(msg)
            headers.update(
                build_auth_headers(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    path=normalized_path,
                    params=request_params,
                    nonce=self.nonce_factory(),
                )
            )

        kwargs: dict[str, object] = {
            "headers": headers,
            "timeout": self.timeout,
        }
        if normalized_method == "GET":
            kwargs["params"] = request_params
        else:
            kwargs["json"] = request_params

        response = self.session.request(normalized_method, url, **kwargs)
        raise_for_response_status(response)
        if not response.content:
            return None

        payload = response.json()
        raise_for_api_error(payload)
        return payload
