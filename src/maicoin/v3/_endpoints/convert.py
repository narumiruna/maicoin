"""Convert REST v3 endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from maicoin.v3._endpoints.base import RestRequester
from maicoin.v3._endpoints.base import compact
from maicoin.v3.models import ConvertOrder


@dataclass(frozen=True, slots=True)
class ConvertEndpoints:
    """Authenticated convert request/parse rules."""

    requester: RestRequester

    async def create_convert(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
    ) -> ConvertOrder:
        payload = await self.requester.request(
            "POST",
            "/api/v3/convert",
            params=compact(
                {
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "from_amount": from_amount,
                    "to_amount": to_amount,
                }
            ),
            auth=True,
        )
        return ConvertOrder.model_validate(payload)

    async def convert(self, sn: str) -> ConvertOrder:
        payload = await self.requester.request("GET", "/api/v3/convert", params={"sn": sn}, auth=True)
        return ConvertOrder.model_validate(payload)

    async def converts(
        self, *, timestamp: int | None = None, order: str | None = None, limit: int | None = None
    ) -> list[ConvertOrder]:
        payload = await self.requester.request(
            "GET",
            "/api/v3/converts",
            params=compact({"timestamp": timestamp, "order": order, "limit": limit}),
            auth=True,
        )
        return [ConvertOrder.model_validate(item) for item in cast("list[object]", payload)]
