"""Convert REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass

from maicoin.v3._endpoints.base import EndpointExecutor
from maicoin.v3._endpoints.base import EndpointSpec
from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3.models.convert import ConvertOrder

CREATE_CONVERT = EndpointSpec("POST", "/api/v3/convert", auth=True)
CONVERT = EndpointSpec("GET", "/api/v3/convert", auth=True)
CONVERTS = EndpointSpec("GET", "/api/v3/converts", auth=True)


@dataclass(frozen=True, slots=True)
class ConvertEndpoints:
    """Authenticated convert request/parse rules."""

    requester: RestRequester

    @property
    def endpoint(self) -> EndpointExecutor:
        return EndpointExecutor(self.requester)

    async def create_convert(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
    ) -> ConvertOrder:
        return await self.endpoint.model(
            CREATE_CONVERT,
            ConvertOrder,
            {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "from_amount": from_amount,
                "to_amount": to_amount,
            },
        )

    async def convert(self, sn: str) -> ConvertOrder:
        return await self.endpoint.model(CONVERT, ConvertOrder, {"sn": sn})

    async def converts(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        return await self.endpoint.model_list(
            CONVERTS,
            ConvertOrder,
            {"timestamp": timestamp, "order": order, "limit": limit},
        )
