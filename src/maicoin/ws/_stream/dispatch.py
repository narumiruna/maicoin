from __future__ import annotations

import asyncio
import inspect

from maicoin.ws._stream.types import DispatchMode
from maicoin.ws._stream.types import Handler
from maicoin.ws._stream.types import HandlerErrorCallback
from maicoin.ws.response import Response


class ResponseDispatcher:
    """Own response dispatch mode rules, handler errors, and task cleanup."""

    def __init__(
        self,
        *,
        dispatch: DispatchMode,
        handlers: list[Handler],
        response_queue: asyncio.Queue[Response],
        on_handler_error: HandlerErrorCallback | None = None,
    ) -> None:
        if dispatch not in {"inline", "task", "queue"}:
            msg = "dispatch must be 'inline', 'task', or 'queue'"
            raise ValueError(msg)

        self.dispatch = dispatch
        self.handlers = handlers
        self.response_queue = response_queue
        self.on_handler_error = on_handler_error
        self._handler_tasks: set[asyncio.Task[object]] = set()

    async def dispatch_response(self, response: Response) -> None:
        if self.dispatch == "queue":
            await self.response_queue.put(response)
            return

        for handler in self.handlers:
            if self.dispatch == "task":
                task = asyncio.create_task(self.call_handler(handler, response))
                self._handler_tasks.add(task)
                task.add_done_callback(self._handler_tasks.discard)
            else:
                await self.call_handler(handler, response)

    async def call_handler(self, handler: Handler, response: Response) -> None:
        try:
            result = handler(response)
            if inspect.isawaitable(result):
                await result
        except Exception as exc:
            if self.on_handler_error is None:
                if self.dispatch == "inline":
                    raise
                return
            result = self.on_handler_error(exc, response)
            if inspect.isawaitable(result):
                await result

    async def cancel_handler_tasks(self) -> None:
        for task in self._handler_tasks:
            task.cancel()
        if self._handler_tasks:
            await asyncio.gather(*self._handler_tasks, return_exceptions=True)
        self._handler_tasks.clear()
