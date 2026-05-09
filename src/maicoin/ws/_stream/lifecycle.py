from __future__ import annotations

import inspect

from maicoin.ws._stream.types import LifecycleCallback


async def call_lifecycle(callback: LifecycleCallback | None, exc: Exception | None) -> None:
    if callback is None:
        return
    result = callback(exc)
    if inspect.isawaitable(result):
        await result
