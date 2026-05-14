from __future__ import annotations

import re
from pathlib import Path

import maicoin.ws as ws

API_LINK_PATTERN = re.compile(r"\[[^\]]+\]\[(maicoin\.(?:v3|ws)(?:\.[A-Za-z_]\w*)+)\]")
MKDOCSTRINGS_TARGET_PATTERN = re.compile(r"^:::\s+(maicoin\.(?:v3|ws)(?:\.[A-Za-z_]\w*)*)", re.MULTILINE)

DOC_SOURCE_ROOTS = (Path("docs/site/content"), Path("src/maicoin"))
REFERENCE_PAGES = (Path("docs/site/content/reference/v3.md"), Path("docs/site/content/reference/ws.md"))
SOURCE_SUFFIXES = {".md", ".py"}


def test_documented_api_links_have_reference_targets() -> None:
    reference_targets = _reference_targets()
    missing_targets = sorted(
        target for target in _api_link_targets() if not _is_covered_by_reference(target, reference_targets)
    )

    assert missing_targets == []


def test_websocket_public_exports_are_listed_on_reference_page() -> None:
    reference_targets = _reference_targets_from(Path("docs/site/content/reference/ws.md"))
    missing_exports = sorted(
        f"maicoin.ws.{name}" for name in ws.__all__ if f"maicoin.ws.{name}" not in reference_targets
    )

    assert missing_exports == []


def _api_link_targets() -> set[str]:
    targets: set[str] = set()
    for root in DOC_SOURCE_ROOTS:
        for path in sorted(root.rglob("*")):
            if path.suffix not in SOURCE_SUFFIXES:
                continue
            targets.update(API_LINK_PATTERN.findall(path.read_text(encoding="utf-8")))
    return targets


def _reference_targets() -> set[str]:
    targets: set[str] = set()
    for path in REFERENCE_PAGES:
        targets.update(_reference_targets_from(path))
    return targets


def _reference_targets_from(path: Path) -> set[str]:
    return set(MKDOCSTRINGS_TARGET_PATTERN.findall(path.read_text(encoding="utf-8")))


def _is_covered_by_reference(target: str, reference_targets: set[str]) -> bool:
    parts = target.split(".")
    return any(".".join(parts[:index]) in reference_targets for index in range(len(parts), 1, -1))
