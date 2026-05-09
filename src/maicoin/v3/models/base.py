from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict


class MaxBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
