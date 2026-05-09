"""Authentication helpers for [MaiCoin MAX REST v3](https://max-api.maicoin.com/doc/v3.html).

MAX expects each authenticated request to carry three headers:

- `X-MAX-ACCESSKEY` — the API access key.
- `X-MAX-PAYLOAD` — a base64-encoded JSON object containing `path`, `nonce`,
  and request parameters.
- `X-MAX-SIGNATURE` — `HMAC-SHA256(api_secret, payload)` as hex.

The functions in this module produce those values. [`Client`][maicoin.v3.Client]
uses them automatically; call them directly only if you are building requests
outside the typed client.
"""

from __future__ import annotations

import base64
import hmac
from collections.abc import Mapping
from datetime import UTC
from datetime import datetime

import orjson


def generate_nonce() -> int:
    """Return the current UTC time as a millisecond UNIX nonce.

    MAX rejects any nonce that is not strictly greater than the previous one
    used by the key, so reusing this helper across processes that share an API
    key can race. Pass a custom `nonce_factory` to [`Client`][maicoin.v3.Client]
    if you need monotonic generation.
    """
    return int(datetime.now(tz=UTC).timestamp() * 1000)


def encode_payload(path: str, params: Mapping[str, object] | None = None, nonce: int | None = None) -> str:
    """Build the base64-encoded payload that goes in the `X-MAX-PAYLOAD` header.

    Args:
        path: Request path beginning with `/`, e.g. `"/api/v3/info"`.
        params: Request parameters merged into the payload (typically the
            query string for GET requests, or the JSON body for POST/DELETE).
        nonce: Millisecond nonce. Generated via [`generate_nonce`][maicoin.v3.generate_nonce]
            when omitted.

    Returns:
        Base64-encoded JSON ready to assign to `X-MAX-PAYLOAD`.
    """
    payload: dict[str, object] = {"nonce": generate_nonce() if nonce is None else nonce}
    if params is not None:
        payload.update(params)
    payload["path"] = path

    json_payload = orjson.dumps(payload)
    return base64.b64encode(json_payload).decode()


def sign_payload(api_secret: str, payload: str) -> str:
    """Return the HMAC-SHA256 hex digest of `payload` keyed with `api_secret`.

    The result is what MAX expects in the `X-MAX-SIGNATURE` header.
    """
    return hmac.new(api_secret.encode(), payload.encode(), digestmod="sha256").hexdigest()


def build_auth_headers(
    api_key: str,
    api_secret: str,
    path: str,
    params: Mapping[str, object] | None = None,
    nonce: int | None = None,
) -> dict[str, str]:
    """Build the full set of MAX authentication headers for a request.

    Args:
        api_key: MAX API access key.
        api_secret: MAX API secret.
        path: Request path beginning with `/`.
        params: Request parameters that will be sent (must match the payload
            actually transmitted, otherwise the signature is rejected).
        nonce: Optional millisecond nonce. Generated when omitted.

    Returns:
        A dict containing `X-MAX-ACCESSKEY`, `X-MAX-PAYLOAD`,
        `X-MAX-SIGNATURE`, and `Content-Type: application/json`.
    """
    payload = encode_payload(path=path, params=params, nonce=nonce)
    return {
        "X-MAX-ACCESSKEY": api_key,
        "X-MAX-PAYLOAD": payload,
        "X-MAX-SIGNATURE": sign_payload(api_secret=api_secret, payload=payload),
        "Content-Type": "application/json",
    }
