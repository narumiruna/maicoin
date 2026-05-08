from __future__ import annotations

import base64
import hmac
import json
from collections.abc import Mapping
from datetime import UTC
from datetime import datetime


def generate_nonce() -> int:
    return int(datetime.now(tz=UTC).timestamp() * 1000)


def encode_payload(path: str, params: Mapping[str, object] | None = None, nonce: int | None = None) -> str:
    payload: dict[str, object] = {"nonce": generate_nonce() if nonce is None else nonce}
    if params is not None:
        payload.update(params)
    payload["path"] = path

    json_payload = json.dumps(payload, separators=(",", ":"))
    return base64.b64encode(json_payload.encode()).decode()


def sign_payload(api_secret: str, payload: str) -> str:
    return hmac.new(api_secret.encode(), payload.encode(), digestmod="sha256").hexdigest()


def build_auth_headers(
    api_key: str,
    api_secret: str,
    path: str,
    params: Mapping[str, object] | None = None,
    nonce: int | None = None,
) -> dict[str, str]:
    payload = encode_payload(path=path, params=params, nonce=nonce)
    return {
        "X-MAX-ACCESSKEY": api_key,
        "X-MAX-PAYLOAD": payload,
        "X-MAX-SIGNATURE": sign_payload(api_secret=api_secret, payload=payload),
        "Content-Type": "application/json",
    }
