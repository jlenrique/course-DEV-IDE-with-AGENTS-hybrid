"""AC-T.3 — no forbidden user-facing leak in coverage-manifest prose."""

from __future__ import annotations

import re
from pathlib import Path

from app.marcus.lesson_plan.coverage_manifest import CoverageManifest, CoverageSummary, CoverageSurface

FILE_TO_SCAN = (
    Path(__file__).resolve().parents[2] / "app" / "marcus" / "lesson_plan" / "coverage_manifest.py"
)
FORBIDDEN = re.compile(r"\b(intake|orchestrator)\b", flags=re.IGNORECASE)


def test_no_forbidden_tokens_in_coverage_manifest_user_facing_surface() -> None:
    for lineno, line in enumerate(FILE_TO_SCAN.read_text(encoding="utf-8").splitlines(), start=1):
        match = FORBIDDEN.search(line)
        assert match is None, f"Forbidden token {match.group()!r} leaked at line {lineno}"

    for model_cls in (CoverageSurface, CoverageSummary, CoverageManifest):
        for field_name, field_info in model_cls.model_fields.items():
            if field_info.description:
                match = FORBIDDEN.search(field_info.description)
                assert match is None, (
                    f"Forbidden token {match.group()!r} leaked in "
                    f"{model_cls.__name__}.{field_name} description"
                )
