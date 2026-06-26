"""No-leak grep test for the LearningObjective family (Story G0-S1, checklist 11).

Forbidden tokens ``intake`` / ``orchestrator`` must not appear in user-facing
field descriptions, the canonical/adapter source, the emitted JSON-Schema
witness, or model_dump output. R1 ruling amendment 17 / R2 rider S-3.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app.marcus.lesson_plan.learning_objective import (
    LearningObjective,
    SourceAdequacy,
    SourceRef,
    learning_objective_json_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

FILES_TO_SCAN = [
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "learning_objective.py",
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "learning_objective_adapters.py",
    REPO_ROOT / "app" / "marcus" / "lesson_plan" / "schema" / "learning_objective.v1.schema.json",
]

FORBIDDEN_TOKEN_PATTERN = re.compile(r"\b(intake|orchestrator)\b", flags=re.IGNORECASE)

EXEMPT_MARKERS = ("# noqa: no-leak-grep", "# internal-taxonomy-exempt")

_MODELS = [LearningObjective, SourceRef, SourceAdequacy]


def test_no_forbidden_tokens_in_field_descriptions() -> None:
    for model_cls in _MODELS:
        for name, field_info in model_cls.model_fields.items():
            if not field_info.description:
                continue
            match = FORBIDDEN_TOKEN_PATTERN.search(field_info.description)
            assert match is None, f"{model_cls.__name__}.{name}: {field_info.description!r}"


@pytest.mark.parametrize(
    "path", FILES_TO_SCAN, ids=lambda p: str(p.relative_to(REPO_ROOT))
)
def test_no_forbidden_tokens_in_scanned_files(path: Path) -> None:
    assert path.exists(), f"Scan target missing: {path}"
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if any(marker in line for marker in EXEMPT_MARKERS):
            continue
        match = FORBIDDEN_TOKEN_PATTERN.search(line)
        assert match is None, (
            f"Forbidden token {match.group()!r} at {path}:{lineno}: {line.strip()!r}"
        )


def test_no_forbidden_tokens_in_emitted_schema() -> None:
    blob = json.dumps(learning_objective_json_schema())
    match = FORBIDDEN_TOKEN_PATTERN.search(blob)
    assert match is None, f"Forbidden token in emitted schema: {match.group() if match else ''}"


def test_no_forbidden_tokens_in_model_dump() -> None:
    lo = LearningObjective(
        objective_id="obj-1",
        statement="Analyze the macro trends",
        status="refined",
        confidence="medium",
        source_refs=[SourceRef(source_id="s1", locator="p1", quoted_span="span")],
        adequacy=SourceAdequacy(verdict="thin", rationale="r", missing=["the assess-leg"]),
    )
    match = FORBIDDEN_TOKEN_PATTERN.search(lo.model_dump_json())
    assert match is None
