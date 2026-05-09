from __future__ import annotations

import asyncio

import pytest

from maicoin.ws import Response
from maicoin.ws._stream.dispatch import ResponseDispatcher

MESSAGE = '{"e":"subscribed","s":[{"channel":"trade","market":"btctwd"}],"i":"client1","T":123456789}'


@pytest.fixture
def response() -> Response:
    return Response.model_validate_json(MESSAGE)


@pytest.mark.anyio
async def test_inline_dispatch_runs_handlers_in_registration_order(response: Response) -> None:
    calls: list[str] = []

    async def first(_response: Response) -> None:
        calls.append("first")

    def second(_response: Response) -> None:
        calls.append("second")

    dispatcher = ResponseDispatcher(
        dispatch="inline",
        handlers=[first, second],
        response_queue=asyncio.Queue(),
    )

    await dispatcher.dispatch_response(response)

    assert calls == ["first", "second"]


@pytest.mark.anyio
async def test_inline_dispatch_reports_handler_errors(response: Response) -> None:
    errors: list[tuple[Exception, Response]] = []

    def fail(_response: Response) -> None:
        raise RuntimeError("boom")

    dispatcher = ResponseDispatcher(
        dispatch="inline",
        handlers=[fail],
        response_queue=asyncio.Queue(),
        on_handler_error=lambda exc, errored_response: errors.append((exc, errored_response)),
    )

    await dispatcher.dispatch_response(response)

    assert [(type(exc), errored_response.event) for exc, errored_response in errors] == [(RuntimeError, "subscribed")]


@pytest.mark.anyio
async def test_queue_dispatch_enqueues_response_without_calling_handlers(response: Response) -> None:
    queue: asyncio.Queue[Response] = asyncio.Queue()

    def fail(_response: Response) -> None:
        raise AssertionError("queue dispatch should not call handlers")

    dispatcher = ResponseDispatcher(
        dispatch="queue",
        handlers=[fail],
        response_queue=queue,
    )

    await dispatcher.dispatch_response(response)

    assert queue.get_nowait() is response


@pytest.mark.anyio
async def test_task_dispatch_cleans_up_cancelled_handler_tasks(response: Response) -> None:
    started = asyncio.Event()

    async def slow(_response: Response) -> None:
        started.set()
        await asyncio.sleep(60)

    dispatcher = ResponseDispatcher(
        dispatch="task",
        handlers=[slow],
        response_queue=asyncio.Queue(),
    )

    await dispatcher.dispatch_response(response)
    await started.wait()
    await dispatcher.cancel_handler_tasks()

    assert dispatcher._handler_tasks == set()
