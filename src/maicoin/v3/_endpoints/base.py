"""Shared internals for REST v3 endpoint families."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from typing import TypeVar
from typing import cast

from pydantic import BaseModel


class RestRequester(Protocol):
    """Minimal seam endpoint families need from the public client."""

    async def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, object] | None = None,
        *,
        auth: bool = False,
    ) -> object: ...


ModelT = TypeVar("ModelT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    """Static MAX REST v3 request metadata for one endpoint."""

    method: str
    path: str
    auth: bool = False

    def resolved_path(self, path_params: Mapping[str, object] | None = None) -> str:
        """Format a path template using endpoint-family path params."""
        if not path_params:
            return self.path
        return self.path.format(**path_params)


@dataclass(frozen=True, slots=True)
class EndpointExecutor:
    """Execute endpoint specs and centralize common response parsing shapes."""

    requester: RestRequester

    async def raw(
        self,
        spec: EndpointSpec,
        params: Mapping[str, object | None] | None = None,
        *,
        path_params: Mapping[str, object] | None = None,
    ) -> object:
        """Execute an endpoint spec with consistent param omission and auth metadata."""
        return await self.requester.request(
            spec.method,
            spec.resolved_path(path_params),
            params=compact(params or {}),
            auth=spec.auth,
        )

    async def model(
        self,
        spec: EndpointSpec,
        model: type[ModelT],
        params: Mapping[str, object | None] | None = None,
        *,
        path_params: Mapping[str, object] | None = None,
    ) -> ModelT:
        """Execute an endpoint and parse a single Pydantic model."""
        payload = await self.raw(spec, params=params, path_params=path_params)
        return model.model_validate(payload)

    async def model_list(
        self,
        spec: EndpointSpec,
        model: type[ModelT],
        params: Mapping[str, object | None] | None = None,
        *,
        path_params: Mapping[str, object] | None = None,
    ) -> list[ModelT]:
        """Execute an endpoint and parse a JSON array of Pydantic models."""
        payload = await self.raw(spec, params=params, path_params=path_params)
        return [model.model_validate(item) for item in cast("list[object]", payload)]

    async def model_mapping(
        self,
        spec: EndpointSpec,
        model: type[ModelT],
        params: Mapping[str, object | None] | None = None,
        *,
        path_params: Mapping[str, object] | None = None,
    ) -> dict[str, ModelT]:
        """Execute an endpoint and parse a JSON object keyed to Pydantic models."""
        payload = await self.raw(spec, params=params, path_params=path_params)
        return {key: model.model_validate(value) for key, value in cast("dict[str, object]", payload).items()}


def compact(params: Mapping[str, object | None]) -> dict[str, object]:
    """Drop None-valued request params while keeping false-y API values."""
    return {key: value for key, value in params.items() if value is not None}


async def iter_id_paginated[PageItemT](  # noqa: C901
    fetch_page: Callable[[int | None, int], Awaitable[Sequence[PageItemT]]],
    item_id: Callable[[PageItemT], int],
    *,
    from_id: int | None,
    page_limit: int,
    max_items: int | None,
    max_pages: int | None,
) -> AsyncIterator[PageItemT]:
    """Iterate MAX id-cursor pages while avoiding cursor-boundary duplicates."""
    if page_limit <= 0:
        msg = "page_limit must be greater than 0"
        raise ValueError(msg)
    if max_items == 0 or max_pages == 0:
        return

    cursor = from_id
    yielded = 0
    seen_ids: set[int] = set()
    page_count = max_pages if max_pages is not None else 2**63

    for page_number in range(page_count):
        page = await fetch_page(cursor, page_limit)
        if not page:
            return

        next_cursor = cursor
        for item in page:
            current_id = item_id(item)
            if current_id in seen_ids:
                continue
            seen_ids.add(current_id)
            yield item
            yielded += 1
            if max_items is not None and yielded >= max_items:
                return
            if next_cursor is None or current_id > next_cursor:
                next_cursor = current_id

        if len(page) < page_limit or page_number + 1 >= page_count:
            return
        if next_cursor == cursor:
            return
        cursor = next_cursor
