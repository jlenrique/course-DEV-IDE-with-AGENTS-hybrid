from __future__ import annotations

import shutil
from pathlib import Path

from app.replay.parity_comparison import (
    DEFAULT_BASELINE_ENVELOPE_PATH,
    DEFAULT_CLONE_RUN_ROOT,
    DEFAULT_PRIMARY_BUNDLE_ROOT,
    _canonical_asset_specs,
    _canonical_asset_specs_from_gary_outbound,
    _canonical_course_context,
    _canonical_course_context_from_run_constants,
    _canonical_module_context,
    _canonical_module_context_from_run_constants,
    _canonical_motion_plan,
    _compare_semantic_lines,
    compare_actual_substrate_parity,
    render_parity_evidence_markdown,
)


def test_compare_actual_substrate_parity_clears_thresholds() -> None:
    report = compare_actual_substrate_parity()
    assert report.tier1_score >= report.tier1_threshold
    assert report.tier2_score >= report.tier2_threshold
    assert report.comparable_artifact_count == 4


def test_run_constants_canonicalize_to_course_context() -> None:
    primary = _canonical_course_context_from_run_constants(
        DEFAULT_PRIMARY_BUNDLE_ROOT / "run-constants.yaml"
    )
    clone = _canonical_course_context(DEFAULT_CLONE_RUN_ROOT / "course_context.yaml")
    assert primary == clone


def test_run_constants_canonicalize_to_module_context() -> None:
    primary = _canonical_module_context_from_run_constants(
        DEFAULT_PRIMARY_BUNDLE_ROOT / "run-constants.yaml"
    )
    clone = _canonical_module_context(DEFAULT_CLONE_RUN_ROOT / "module_context.yaml")
    assert primary == clone


def test_gary_outbound_canonicalizes_to_asset_specs() -> None:
    primary = _canonical_asset_specs_from_gary_outbound(
        DEFAULT_PRIMARY_BUNDLE_ROOT / "gary-outbound-envelope.yaml"
    )
    clone = _canonical_asset_specs(DEFAULT_CLONE_RUN_ROOT / "asset_specs.yaml")
    assert primary == clone


def test_motion_plan_canonicalization_keeps_shared_control_plane_only() -> None:
    primary = _canonical_motion_plan(DEFAULT_PRIMARY_BUNDLE_ROOT / "motion_plan.yaml")
    clone = _canonical_motion_plan(DEFAULT_CLONE_RUN_ROOT / "motion_plan.yaml")
    assert primary == clone


def test_semantic_match_normalizes_run_ids_paths_and_timestamps() -> None:
    primary = {
        "run_id": "C1-M1-PRES-20260419B",
        "path": "C:\\repo\\course-content\\foo\\bar.md",
        "captured_at": "2026-04-26T17:00:00Z",
    }
    clone = {
        "run_id": "C1-M1-PRES-20260501A",
        "path": "D:\\other\\course-content\\foo\\bar.md",
        "captured_at": "2026-04-30T09:15:00+00:00",
    }
    score, matched, total, *_ = _compare_semantic_lines(primary, clone)
    assert score == 1.0
    assert matched == total == 3


def test_missing_clone_artifact_reduces_tier1_score() -> None:
    sandbox_root = Path(".tmp") / "parity_comparison_missing_clone"
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    primary_root = sandbox_root / "primary"
    clone_root = sandbox_root / "clone"
    primary_root.mkdir(parents=True)
    clone_root.mkdir(parents=True)

    try:
        for relative_path in (
            "run-constants.yaml",
            "gary-outbound-envelope.yaml",
            "motion_plan.yaml",
        ):
            shutil.copy(DEFAULT_PRIMARY_BUNDLE_ROOT / relative_path, primary_root / relative_path)
        for relative_path in ("course_context.yaml", "module_context.yaml", "asset_specs.yaml"):
            shutil.copy(DEFAULT_CLONE_RUN_ROOT / relative_path, clone_root / relative_path)

        report = compare_actual_substrate_parity(
            primary_bundle_root=primary_root,
            clone_run_root=clone_root,
            baseline_envelope_path=DEFAULT_BASELINE_ENVELOPE_PATH,
        )
        assert report.tier1_score == 0.75
        assert any(not result.tier1_present for result in report.artifact_results)
    finally:
        shutil.rmtree(sandbox_root)


def test_rendered_markdown_includes_tier_headers_and_conditional_note() -> None:
    report = compare_actual_substrate_parity()
    markdown = render_parity_evidence_markdown(report)
    assert "## Tier 1" in markdown
    assert "## Tier 2" in markdown
    assert "TIER 1 Score:" in markdown
    assert "TIER 2 Score:" in markdown
    assert "AC-A remains conditional" in markdown
