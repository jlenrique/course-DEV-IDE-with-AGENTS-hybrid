"""Story 32-2a: emit_coverage_manifest regenerates green on current repo state.

AC-T.1 — no CoverageManifestError on default inventory.
AC-T.2 — step 11 factory returns real ProducedAsset; honest plan-ref False/False.
AC-T.3 — step 12 module_path is quinn_r_gate.py; factory returns QuinnRUnitVerdict.
AC-T.4 — step 13 factory returns QuinnRTwoBranchResult with nested plan_ref.
AC-T.5 — honest summary invariants (robust to 30-4 in-flight landings).
"""

from __future__ import annotations

from pathlib import Path

from app.marcus.lesson_plan.coverage_manifest import (
    DEFAULT_COVERAGE_INVENTORY,
    build_coverage_manifest,
    emit_coverage_manifest,
    verify_plan_ref_fields,
)
from app.marcus.lesson_plan.produced_asset import ProducedAsset
from app.marcus.lesson_plan.quinn_r_gate import QuinnRTwoBranchResult, QuinnRUnitVerdict


def _entry_by_step_id(step_id: str):
    for entry in DEFAULT_COVERAGE_INVENTORY:
        if entry.step_id == step_id:
            return entry
    raise AssertionError(f"step {step_id!r} missing from DEFAULT_COVERAGE_INVENTORY")


def test_emit_coverage_manifest_no_crash_on_current_repo(tmp_path: Path) -> None:
    output_path = tmp_path / "manifest.json"
    manifest = emit_coverage_manifest(output_path=output_path)

    assert output_path.exists()
    assert manifest.summary.total_surfaces == 9


def test_step_11_factory_returns_real_blueprint_producer_output() -> None:
    entry = _entry_by_step_id("11")
    assert entry.sample_factory is not None
    sample = entry.sample_factory()

    assert isinstance(sample, ProducedAsset)
    assert verify_plan_ref_fields(sample, "nested-plan-ref") == (False, False)


def test_step_12_module_path_fix_and_unit_verdict_factory() -> None:
    entry = _entry_by_step_id("12")

    # Prefix canonicalized to app/marcus in the 2026-06-12 drift micro-batch
    # (namespace retired 2026-05-07; the stale string crashed
    # build_coverage_manifest via the done-but-module-missing drift check).
    assert entry.module_path == "app/marcus/lesson_plan/quinn_r_gate.py"
    assert entry.sample_factory is not None
    sample = entry.sample_factory()
    assert isinstance(sample, QuinnRUnitVerdict)
    assert verify_plan_ref_fields(sample, "nested-plan-ref") == (False, False)


def test_step_13_factory_returns_two_branch_result_with_nested_plan_ref() -> None:
    entry = _entry_by_step_id("13")
    assert entry.sample_factory is not None
    sample = entry.sample_factory()

    assert isinstance(sample, QuinnRTwoBranchResult)
    has_rev, has_digest = verify_plan_ref_fields(sample, "nested-plan-ref")
    assert has_rev is True
    assert has_digest is True


def test_honest_summary_invariants_on_current_repo() -> None:
    manifest = build_coverage_manifest()
    s = manifest.summary

    assert s.total_surfaces == 9
    assert s.implemented_surfaces + s.pending_surfaces + s.deferred_surfaces == s.total_surfaces
    assert s.implemented_surfaces >= 3
    assert s.surfaces_with_full_plan_ref_coverage >= 1
    assert s.surfaces_missing_one_or_both_fields >= 2
    assert s.trial_ready is False
