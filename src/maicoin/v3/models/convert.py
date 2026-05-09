from __future__ import annotations

from maicoin.v3.models.base import MaxBaseModel


class ConvertOrder(MaxBaseModel):
    sn: str
    from_currency: str
    from_amount: str
    to_currency: str
    to_amount: str
    fee: str
    fee_currency: str
    fee_in_twd: str
    created_at: int
