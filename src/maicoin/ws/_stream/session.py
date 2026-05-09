from __future__ import annotations

from maicoin.ws._stream.dispatch import ResponseDispatcher
from maicoin.ws._stream.lifecycle import call_lifecycle
from maicoin.ws._stream.types import LifecycleCallback
from maicoin.ws._stream.types import WebSocketConnection
from maicoin.ws.request import Request
from maicoin.ws.response import Response


class ConnectedSession:
    """Run one connected websocket session: replay requests, receive, parse, dispatch."""

    def __init__(
        self,
        *,
        requests: list[Request],
        dispatcher: ResponseDispatcher,
        on_connected: LifecycleCallback | None = None,
    ) -> None:
        self.requests = requests
        self.dispatcher = dispatcher
        self.on_connected = on_connected

    async def run(self, ws: WebSocketConnection) -> None:
        for request in self.requests:
            await ws.send(request.message())
        await call_lifecycle(self.on_connected, None)

        while True:
            data = await ws.recv()
            response = Response.model_validate_json(data)
            await self.dispatcher.dispatch_response(response)
