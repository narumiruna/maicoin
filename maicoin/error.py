from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .event import Event


@dataclass
class Error:
    event: Event
    errors: List[str]
    id: str
    created_at: str

    @classmethod
    def from_dict(cls, d: dict) -> Error:
        return cls(
            Event(d.get('e')),
            d.get('E'),
            d.get('i'),
            d.get('T'),
        )
