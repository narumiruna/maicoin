import base64
import json

from maicoin.v3.auth import build_auth_headers
from maicoin.v3.auth import encode_payload
from maicoin.v3.auth import sign_payload


def test_encode_payload_with_fixed_nonce() -> None:
    payload = encode_payload(
        path="/api/v3/order",
        params={"market": "btctwd", "side": "bid"},
        nonce=123456,
    )

    assert payload == "eyJub25jZSI6MTIzNDU2LCJtYXJrZXQiOiJidGN0d2QiLCJzaWRlIjoiYmlkIiwicGF0aCI6Ii9hcGkvdjMvb3JkZXIifQ=="
    assert json.loads(base64.b64decode(payload).decode()) == {
        "nonce": 123456,
        "market": "btctwd",
        "side": "bid",
        "path": "/api/v3/order",
    }


def test_sign_payload() -> None:
    payload = "eyJub25jZSI6MTIzNDU2LCJtYXJrZXQiOiJidGN0d2QiLCJzaWRlIjoiYmlkIiwicGF0aCI6Ii9hcGkvdjMvb3JkZXIifQ=="

    assert sign_payload(api_secret="secret", payload=payload) == (
        "a9bf57e0ad199f4ca4325cd0a9af0a82193cb103b1ba5eaaa55b58f79d408ab6"
    )


def test_build_auth_headers() -> None:
    headers = build_auth_headers(
        api_key="key",
        api_secret="secret",
        path="/api/v3/order",
        params={"market": "btctwd", "side": "bid"},
        nonce=123456,
    )

    assert headers == {
        "X-MAX-ACCESSKEY": "key",
        "X-MAX-PAYLOAD": (
            "eyJub25jZSI6MTIzNDU2LCJtYXJrZXQiOiJidGN0d2QiLCJzaWRlIjoiYmlkIiwicGF0aCI6Ii9hcGkvdjMvb3JkZXIifQ=="
        ),
        "X-MAX-SIGNATURE": "a9bf57e0ad199f4ca4325cd0a9af0a82193cb103b1ba5eaaa55b58f79d408ab6",
        "Content-Type": "application/json",
    }
