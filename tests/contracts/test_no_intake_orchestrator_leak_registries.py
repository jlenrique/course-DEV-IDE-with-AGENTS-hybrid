"""AC-T.8 — No-leak grep over the four 31-3 modules (R1 amendment 17 / R2 rider S-3).

Forbidden tokens in user-facing strings: ``intake``, ``orchestrator``
(case-insensitive). Internal module names (e.g., ``marcus-intake`` /
``marcus-orchestrator`` in ``log.py``'s ``WriterIdentity``) are NOT present in
31-3 modules — they're internal taxonomy of 31-2 and out-of-scope for this
scan.

Scans:
    - marcus/lesson_plan/modality_registry.py
    - marcus/lesson_plan/component_type_registry.py
    - marcus/lesson_plan/modality_producer.py
    - marcus/lesson_plan/produced_asset.py

At each file-line granularity AND on Pydantic ``description=`` values extracted
from model fields.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.marcus.lesson_plan.component_type_registry import ComponentTypeEntry
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY, ModalityEntry
from app.marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext

REPO_ROOT = Path(__file__).resolve().parents[2]

FILES_TO_SCAN: list[Path] = [
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "modality_registry.py",
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "component_type_registry.py",
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "modality_producer.py",
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "produced_asset.py",
]

FORBIDDEN_TOKEN_PATTERN = re.compile(
    r"\b(intake|orchestrator)\b",
    flags=re.IGNORECASE,
)

EXEMPT_MARKERS = (
    "# noqa: no-leak-grep",
    "# internal-taxonomy-exempt",
)


@pytest.mark.parametrize(
    "path", FILES_TO_SCAN, ids=lambda p: p.name
)
def test_no_forbidden_tokens_in_file(path: Path) -> None:
    assert path.exists(), f"Scan target missing: {path}"
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if any(marker in line for marker in EXEMPT_MARKERS):
            continue
        match = FORBIDDEN_TOKEN_PATTERN.search(line)
        assert match is None, (
            f"Forbidden token {match.group()!r} in {path.name}:{lineno}: "
            f"{line.strip()!r}. Add '# noqa: no-leak-grep' if line is "
            f"internal-only."
        )


# ---------------------------------------------------------------------------
# Pydantic field-description scans
# ---------------------------------------------------------------------------


def _field_descriptions_from_model(model_cls) -> list[tuple[str, str]]:
    pairs = []
    for name, field_info in model_cls.model_fields.items():
        if field_info.description:
            pairs.append((name, field_info.description))
    return pairs


@pytest.mark.parametrize(
    "model_cls",
    [ModalityEntry, ComponentTypeEntry, ProductionContext, ProducedAsset],
    ids=lambda m: m.__name__,
)
def test_no_forbidden_tokens_in_field_descriptions(model_cls) -> None:
    for field_name, desc in _field_descriptions_from_model(model_cls):
        match = FORBIDDEN_TOKEN_PATTERN.search(desc)
        assert match is None, (
            f"Forbidden token {match.group()!r} in {model_cls.__name__}."
            f"{field_name} description: {desc!r}"
        )


def test_no_forbidden_tokens_in_registry_entry_descriptions() -> None:
    """ModalityEntry.description literals — scan every seeded entry."""
    for key, entry in MODALITY_REGISTRY.items():
        match = FORBIDDEN_TOKEN_PATTERN.search(entry.description)
        assert match is None, (
            f"Forbidden token {match.group()!r} in "
            f"MODALITY_REGISTRY[{key!r}].description: {entry.description!r}"
        )


def test_no_forbidden_tokens_in_model_dump_output() -> None:
    """Round-trip via model_dump_json for belt-and-suspenders."""
    for entry in MODALITY_REGISTRY.values():
        dumped = entry.model_dump_json()
        match = FORBIDDEN_TOKEN_PATTERN.search(dumped)
        assert match is None, (
            f"Forbidden token {match.group()!r} in model_dump_json output "
            f"for MODALITY_REGISTRY entry: {dumped}"
        )
