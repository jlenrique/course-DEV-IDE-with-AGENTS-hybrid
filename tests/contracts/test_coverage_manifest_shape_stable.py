"""AC-T.1 + AC-C.1 — coverage-manifest shape and changelog gate."""

from __future__ import annotations

from pathlib import Path

import app.marcus.lesson_plan.coverage_manifest as cm_module
from app.marcus.lesson_plan.coverage_manifest import (
    SCHEMA_VERSION,
    CoverageManifest,
    CoverageSummary,
    CoverageSurface,
)

CHANGELOG = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


def test_coverage_manifest_public_surface_and_changelog_are_pinned() -> None:
    assert SCHEMA_VERSION == "1.0"
    assert set(cm_module.__all__) == {
        "COVERAGE_MANIFEST_PATH",
        "CoverageInventoryEntry",
        "CoverageManifest",
        "CoverageManifestError",
        "CoverageSummary",
        "CoverageSurface",
        "DEFAULT_COVERAGE_INVENTORY",
        "SCHEMA_VERSION",
        "build_coverage_manifest",
        "emit_coverage_manifest",
        "render_coverage_manifest_json",
        "summarize_surfaces",
        "verify_assert_plan_fresh_usage",
        "verify_plan_ref_fields",
    }
    assert set(CoverageSurface.model_fields.keys()) == {
        "step_id",
        "surface_name",
        "owner_story_key",
        "module_path",
        "artifact_kind",
        "plan_ref_mode",
        "has_lesson_plan_revision",
        "has_lesson_plan_digest",
        "assert_plan_fresh_required",
        "assert_plan_fresh_verified",
        "status",
        "notes",
    }
    assert set(CoverageSummary.model_fields.keys()) == {
        "total_surfaces",
        "implemented_surfaces",
        "pending_surfaces",
        "deferred_surfaces",
        "surfaces_with_full_plan_ref_coverage",
        "surfaces_missing_one_or_both_fields",
        "surfaces_missing_freshness_gate_verification",
        "trial_ready",
    }
    assert set(CoverageManifest.model_fields.keys()) == {
        "schema_version",
        "generated_at",
        "source_story_key",
        "surfaces",
        "summary",
    }
    assert "Coverage Manifest v1.0" in CHANGELOG.read_text(encoding="utf-8")
