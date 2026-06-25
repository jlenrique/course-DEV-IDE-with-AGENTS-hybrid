"""No-leak grep test for the CollateralSpec family (Braid S1, AC-7 / checklist §11).

Forbidden tokens (case-insensitive, word-boundary): ``intake``, ``orchestrator``.
Marcus is one voice. Scans every Field(description=...), the source module, the
emitted JSON Schema, model_dump_json() output, and the CHANGELOG entry.

RED-first: written before collateral_spec.py exists.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.marcus.lesson_plan.collateral_spec import (
    CollateralSpec,
    DepthDeltaContract,
    Exercise,
    ResearchEnrichmentGoal,
    WorkbookSection,
    WorkbookSpec,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

MODULE_PATH = REPO_ROOT / "app" / "marcus" / "lesson_plan" / "collateral_spec.py"
SCHEMA_PATH = (
    REPO_ROOT
    / "app"
    / "marcus"
    / "lesson_plan"
    / "schema"
    / "collateral_spec.v1.schema.json"
)
CHANGELOG_PATH = (
    REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "SCHEMA_CHANGELOG.md"
)

FORBIDDEN = re.compile(r"\b(intake|orchestrator)\b", flags=re.IGNORECASE)
EXEMPT_MARKERS = ("# noqa: no-leak-grep", "# internal-taxonomy-exempt")

_FAMILY = [
    CollateralSpec,
    WorkbookSpec,
    WorkbookSection,
    DepthDeltaContract,
    Exercise,
    ResearchEnrichmentGoal,
]


def test_no_forbidden_tokens_in_field_descriptions() -> None:
    for model_cls in _FAMILY:
        for name, field in model_cls.model_fields.items():
            if field.description:
                match = FORBIDDEN.search(field.description)
                assert match is None, (
                    f"forbidden token {match.group()!r} in "
                    f"{model_cls.__name__}.{name} description"
                )


def test_no_forbidden_tokens_in_source_module() -> None:
    for lineno, line in enumerate(
        MODULE_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if any(marker in line for marker in EXEMPT_MARKERS):
            continue
        match = FORBIDDEN.search(line)
        assert match is None, (
            f"forbidden token {match.group()!r} in {MODULE_PATH.name}:{lineno}"
        )


def test_no_forbidden_tokens_in_emitted_schema() -> None:
    match = FORBIDDEN.search(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert match is None, f"forbidden token in {SCHEMA_PATH.name}: {match!r}"


def test_no_forbidden_tokens_in_model_dump_output() -> None:
    spec = CollateralSpec(declaration="none")
    match = FORBIDDEN.search(spec.model_dump_json())
    assert match is None


def test_changelog_collateral_entry_has_no_forbidden_tokens() -> None:
    text = CHANGELOG_PATH.read_text(encoding="utf-8")
    marker = "CollateralSpec"
    assert marker in text, "CollateralSpec CHANGELOG entry missing"
    start = text.index(marker)
    # Scan from the family heading to the next top-level heading (or EOF).
    rest = text[start:]
    end = rest.find("\n## ", 1)
    block = rest if end == -1 else rest[:end]
    for line in block.splitlines():
        if any(m in line for m in EXEMPT_MARKERS):
            continue
        match = FORBIDDEN.search(line)
        assert match is None, f"forbidden token in CollateralSpec CHANGELOG block: {line!r}"
